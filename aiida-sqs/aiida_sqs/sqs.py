# aiida_sqs/sqs.py
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from icet import ClusterSpace
from icet.tools.structure_generation import generate_sqs
from ase.build import sort
from ase.neighborlist import neighbor_list
import math

def cutoff_calculator(structure, cutoff=5.0):
    distances = math.ceil(
        neighbor_list('d', structure, cutoff=cutoff, self_interaction=False).min()
    )
    return [distances * 3, distances * 2]

def generate_sqs_structures(structure_data, sub_from, sub_to,
                             concentrations=[0.25, 0.5, 0.75],
                             max_size=16, max_steps=10000, symprec=1e-5):
    """Generate SQS structures for given concentrations (non-AiiDA version)."""
    result = {}
    structure_ini_pmg = Structure.from_dict(structure_data)
    structure_ini = AseAtomsAdaptor.get_atoms(structure_ini_pmg)
    result["initial_formula"] = structure_ini.get_chemical_formula()

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
            sqs_pmg = AseAtomsAdaptor.get_structure(sorted_sqs)
            for site in sqs_pmg.sites:
                site.label = None
            sqs_structures[conc_key] = {
                "concentration": conc_dict,
                "formula": sorted_sqs.get_chemical_formula(),
                "structure": sqs_pmg
            }
        except Exception:
            continue
    result["sqs_structures"] = sqs_structures
    return sqs_structures, result
