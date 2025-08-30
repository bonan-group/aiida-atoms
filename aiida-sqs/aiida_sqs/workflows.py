from aiida.engine import WorkChain, calcfunction
from aiida.orm import StructureData, Dict, List, Str, Int, Float
from aiida.common import AttributeDict
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from icet import ClusterSpace
from icet.tools.structure_generation import generate_sqs
from ase.build import sort
import math
from ase.neighborlist import neighbor_list

@calcfunction
def cutoff_calculator(structure: StructureData, cutoff: Float = None) -> List:
    """Calculate minimum interatomic distance and determine cutoffs."""
    if cutoff is None:
        cutoff = Float(5.0)  
    ase_structure = structure.get_ase()
    distances = math.ceil(
        neighbor_list('d', ase_structure, cutoff=cutoff.value, self_interaction=False).min()
    )
    return List(list=[distances * 3, distances * 2])


class SQSWorkChain(WorkChain):
    """WorkChain to generate Special Quasi-random Structures (SQS) using icet."""

    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input('structure', valid_type=StructureData, help='Input crystal structure')
        spec.input('sub_from', valid_type=Str, help='Element to substitute')
        spec.input('sub_to', valid_type=Str, help='Element to substitute with')
        spec.input('concentrations', valid_type=List, default=lambda: List(list=[0.25, 0.5, 0.75]),
                  help='List of target concentrations')
        spec.input('max_size', valid_type=Int, default=lambda: Int(16),
                  help='Maximum supercell size')
        spec.input('max_steps', valid_type=Int, default=lambda: Int(10000),
                  help='Maximum Monte Carlo steps')
        spec.input('symprec', valid_type=Float, default=lambda: Float(1e-5),
                  help='Symmetry precision for ClusterSpace')
        spec.output('sqs_structures', valid_type=Dict, help='Generated SQS structures')
        spec.output('initial_formula', valid_type=Str, help='Initial structure formula')
        spec.exit_code(400, 'ERROR_INVALID_REPLACEMENT_PAIRS',
                       message='No valid replacement pairs for substitution')
        spec.outline(
            cls.setup,
            cls.generate_sqs,
            cls.finalize,
        )

    def setup(self):
        """Initialize context and compute cutoffs."""
        self.ctx.inputs = AttributeDict({
            'structure': self.inputs.structure,
            'sub_from': self.inputs.sub_from.value,
            'sub_to': self.inputs.sub_to.value,
            'concentrations': self.inputs.concentrations.get_list(),
            'max_size': self.inputs.max_size.value,
            'max_steps': self.inputs.max_steps.value,
            'symprec': self.inputs.symprec.value,
        })
        self.ctx.cutoffs = cutoff_calculator(self.ctx.inputs.structure)

    def generate_sqs(self):
        """Generate SQS structures for given concentrations."""
        structure_pmg = self.ctx.inputs.structure.get_pymatgen()
        structure_ase = AseAtomsAdaptor.get_atoms(structure_pmg)
        result = {'initial_formula': structure_ase.get_chemical_formula()}
        sqs_structures = {}

        merged_symbols = []
        for symbol in structure_ase.get_chemical_symbols():
            merged_symbols.append(
                [self.ctx.inputs.sub_from, self.ctx.inputs.sub_to]
                if symbol == self.ctx.inputs.sub_from else [symbol]
            )

        try:
            cs = ClusterSpace(
                structure_ase,
                self.ctx.cutoffs.get_list(),
                merged_symbols,
                symprec=self.ctx.inputs.symprec
            )
        except RuntimeError:
            cs = ClusterSpace(
                structure_ase,
                self.ctx.cutoffs.get_list(),
                merged_symbols,
                symprec=1e-4
            )

        replacement_pairs = [pair for pair in merged_symbols if len(pair) == 2]
        if not replacement_pairs or len(set(tuple(x) for x in replacement_pairs)) != 1:
            self.report(f"No valid replacement pairs for {self.ctx.inputs.sub_from} -> {self.ctx.inputs.sub_to}")
            return self.exit_codes.ERROR_INVALID_REPLACEMENT_PAIRS

        elem_a, elem_b = replacement_pairs[0]
        concentration_gradients = [
            {elem_a: a, elem_b: 1 - a} for a in self.ctx.inputs.concentrations
        ]

        for conc_dict in concentration_gradients:
            conc_key = f"{elem_a}_{conc_dict[elem_a]:.2f}_{elem_b}_{conc_dict[elem_b]:.2f}"
            try:
                sqs_atoms = generate_sqs(
                    cluster_space=cs,
                    max_size=self.ctx.inputs.max_size,
                    include_smaller_cells=True,
                    target_concentrations=conc_dict,
                    n_steps=self.ctx.inputs.max_steps
                )
                sorted_sqs = sort(sqs_atoms)
                sqs_pmg = AseAtomsAdaptor.get_structure(sorted_sqs)
                for site in sqs_pmg.sites:
                    site.label = None
                sqs_structure = StructureData(pymatgen=sqs_pmg).store()
                sqs_structures[conc_key] = {
                    'concentration': conc_dict,
                    'formula': sorted_sqs.get_chemical_formula(),
                    'structure_uuid': sqs_structure.uuid
                }
            except Exception as e:
                sqs_structures[conc_key] = {'error': str(e)}
                self.report(f"Failed to generate SQS for {conc_key}: {str(e)}")
                continue

        self.ctx.result = result
        self.ctx.result['sqs_structures'] = sqs_structures

    def finalize(self):
        """Output the results safely to AiiDA Dict."""
        sqs_structures_safe = {}

        for key, value in self.ctx.result['sqs_structures'].items():
            safe_key = key.replace('.', '_')
            safe_value = {}
            for k, v in value.items():
                if hasattr(v, 'uuid'):
                    safe_value[k] = str(v.uuid)
                else:
                    safe_value[k] = v
            sqs_structures_safe[safe_key] = safe_value

        self.out('initial_formula', Str(self.ctx.result['initial_formula']).store())
        self.out('sqs_structures', Dict(dict=sqs_structures_safe).store())  
