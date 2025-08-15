import math
import numpy as np
from aiida.engine import WorkChain, ToContext
from aiida import orm
from aiida_vasp.workchains.v2.relax import VaspRelaxWorkChain
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.core import Structure
from ase.neighborlist import neighbor_list
from icet import ClusterSpace
from icet.tools.structure_generation import generate_sqs
from ase.build import sort

def cutoff_calculator(structure, cutoff=5.0):
    """
    Calculate the minimum interatomic neighbor distance for a given structure 
    and determine suitable cutoff distances.
    """
    distances = math.ceil(
        neighbor_list('d', structure, cutoff=cutoff, self_interaction=False).min()
    )
    cutoffs = [distances * 3, distances * 2]
    return cutoffs


def generate_sqs_structures(structure_data, sub_from, sub_to,
                             concentrations=[0.25, 0.5, 0.75],
                             max_size=16, max_steps=10000, symprec=1e-5):
    """Generate SQS structures for given concentrations."""
    result = {}
    sqs_results = {}

    structure_ini_pmg = Structure.from_dict(structure_data)
    structure_ini = AseAtomsAdaptor.get_atoms(structure_ini_pmg)
    formula = structure_ini.get_chemical_formula()
    result["initial_formula"] = formula

    merged_symbols = []
    for symbol in structure_ini.get_chemical_symbols():
        merged_symbols.append([sub_from, sub_to] if symbol == sub_from else [symbol])

    cutoffs = cutoff_calculator(structure_ini)

    try:
        cs = ClusterSpace(structure_ini, cutoffs, merged_symbols, symprec=symprec)
    except RuntimeError:
        cs = ClusterSpace(structure_ini, cutoffs, merged_symbols, symprec=1e-4)

    replacement_pairs = [pair for pair in merged_symbols if len(pair) == 2]
    if not replacement_pairs or len(set(tuple(x) for x in replacement_pairs)) != 1:
        return {}, {"error": f"No valid replacement pairs for {sub_from} -> {sub_to}"}

    elem_a, elem_b = replacement_pairs[0]
    concentration_gradients = [{elem_a: a, elem_b: 1-a} for a in concentrations]

    sqs_structures = {}
    for conc_dict in concentration_gradients:
        conc_key = f"{elem_a}_{conc_dict[elem_a]:.2f}_{elem_b}_{conc_dict[elem_b]:.2f}"
        try:
            sqs_atoms = generate_sqs(
                cluster_space=cs,
                max_size=max_size,
                include_smaller_cells=True,
                target_concentrations=conc_dict,
                n_steps=max_steps
            )
            sorted_sqs = sort(sqs_atoms)
            conc = conc_dict[elem_a]
            sqs_results[f'{conc}'] = sorted_sqs
            sqs_pmg = AseAtomsAdaptor.get_structure(sorted_sqs)
            for site in sqs_pmg.sites:
                site.label = None
            sqs_structures[conc_key] = {
                "concentration": {elem_a: conc_dict[elem_a], elem_b: conc_dict[elem_b]},
                "formula": sorted_sqs.get_chemical_formula(),
                "structure": sqs_pmg
            }
        except Exception:
            continue
    result["sqs_structures"] = sqs_structures
    return sqs_results, result


def get_formation_energy(energies):
    """
    Compute the formation energies for a set of energies.
    """
    # Sort the energies by concentration
    keys_fraction = [0.00, 0.25, 0.50, 0.75, 1.00]
    sorted_items = sorted(energies.items(), key=lambda x: x[1])
    energy_dict = {k: v for k, (_, v) in zip(keys_fraction, sorted_items)}

    # Calculate the formation energies.
    sorted_keys = sorted(energy_dict.keys())
    sorted_values = [energy_dict[key] for key in sorted_keys]
    x = np.array(sorted_keys, dtype=float)
    y = np.array(sorted_values)
    h = y - (1 - x) * y[0] - x * y[-1]

    return {str(xi): hi for xi, hi in zip(x, h)}


class SQSEnergyWorkChain(WorkChain):
    """
    Workchain to compute the formation energies of SQS structures.
    """

    _base_workchain = VaspRelaxWorkChain

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input("structure", valid_type=orm.StructureData, help="Initial structure")
        spec.input("sub_from", valid_type=orm.Str, help="Element to be replaced")
        spec.input("sub_to", valid_type=orm.Str, help="Element to replace with")
        spec.expose_inputs(VaspRelaxWorkChain, 'relax')
        spec.output("formation_energies", valid_type=orm.Dict, help="Formation energies for each structure")
        spec.output("energies", valid_type=orm.Dict, help="Energies for each structure")
        spec.output("structures", valid_type=orm.List, help="Structures after relaxation")

        spec.outline(
            cls.setup,
            cls.generate_structures,
            cls.run_relaxations,
            cls.compute_formation_energies
        )

    def setup(self):
        self.ctx.relax_inputs = self.exposed_inputs(VaspRelaxWorkChain, 'relax')
        self.ctx.energy_dict = {}
        self.ctx.structure_dict = {}
        self.ctx.workchains = {}

    def generate_structures(self):
        """
        Generate the substituted and SQS structures.
        """
        self.report("Generating structures...")

        # Initial structure
        self.ctx.structure_dict["origin"] = self.inputs.structure

        # Substituted structure
        pmg_struct = self.inputs.structure.get_pymatgen()
        replaced = pmg_struct.copy()
        replaced.replace_species({self.inputs.sub_from.value: self.inputs.sub_to.value})
        self.ctx.structure_dict["substituted"] = orm.StructureData(pymatgen=replaced)

        # Generate SQS structures
        sqs_results, _ = generate_sqs_structures(
            pmg_struct.as_dict(),
            self.inputs.sub_from.value,
            self.inputs.sub_to.value,
            concentrations=[0.25, 0.5, 0.75]
        )

        for conc, ase_struct in sqs_results.items():
            pmg_sqs = AseAtomsAdaptor.get_structure(ase_struct)
            self.ctx.structure_dict[str(conc)] = orm.StructureData(pymatgen=pmg_sqs)

    def run_relaxations(self):
        """
        Submit the relaxation workchains for all structures.
        """
        self.report("Submitting relaxation workchains...")
        launchd_calculations = {}
        inputs = self.ctx.relax_inputs
        base_relax_settings = inputs.relax_settings.get_dict()

        for key, struct in self.ctx.structure_dict.items():
            inputs.structure = struct
            relax_settings = base_relax_settings.copy()
            relax_settings['label'] = f'relax_{key}'
            inputs.relax_settings = orm.Dict(dict=relax_settings)
            running = self.submit(self._base_workchain, **inputs)
            launchd_calculations[key] = running
        return ToContext(**launchd_calculations)


    def compute_formation_energies(self):
        """
        Compute the formation energies for all structures.
        """
        for key, wc in self.ctx.workchains.items():
            if wc.is_finished_ok:
                tot_energy = wc.outputs.misc["total_energies"]["energy_extrapolated"]
                n_atoms = len(wc.outputs.relax.structure.sites)
                self.ctx.energy_dict[key] = tot_energy / n_atoms

        # Compute the formation energies.
        formation_energies = get_formation_energy(self.ctx.energy_dict)

        # Save the outputs.
        self.out("energies", orm.Dict(dict=self.ctx.energy_dict))
        self.out("formation_energies", orm.Dict(dict=formation_energies))
        self.out("structures", orm.List(list=[wc.outputs.relax.structure for wc in self.ctx.workchains.values()
                                              if hasattr(wc, "outputs") and "relax" in wc.outputs]))
