import click
import json
import pathlib
from pymatgen.core import Structure
from aiida.cmdline.utils.decorators import with_dbenv
from aiida.engine import run_get_node
from aiida.orm import StructureData, Str, List, Int, Float

from .workflows import SQSWorkChain

@click.group("aiida-sqs")
def cli():
    """CLI for aiida-sqs plugin"""
    pass

@cli.command("generate")
@click.option("--structure", "structure_file", type=click.Path(exists=True, path_type=pathlib.Path),
              required=True, help="Input structure file (.json from pymatgen or CIF).")
@click.option("--sub-from", "sub_from", required=True, help="Element to substitute.")
@click.option("--sub-to", "sub_to", required=True, help="Element to substitute with.")
@click.option("--concentrations", "-c", multiple=True, type=float, default=[0.25, 0.5, 0.75],
              help="List of concentrations (e.g. -c 0.25 -c 0.5).")
@click.option("--max-size", default=16, help="Maximum supercell size.")
@click.option("--max-steps", default=10000, help="Maximum Monte Carlo steps.")
@click.option("--symprec", default=1e-5, type=float, help="Symmetry precision for ClusterSpace.")
@click.option("--output", "-o", type=click.Path(path_type=pathlib.Path), default="sqs_results.json",
              help="Output file to save results.")
@click.option("--store/--no-store", default=True,
    help="Store results in AiiDA database (default: True). Use --no-store for local JSON only."
)
@with_dbenv()
def generate_cmd(structure_file, sub_from, sub_to, concentrations, max_size, max_steps, symprec, output, store):
    """Generate SQS structures from a given structure."""
    # Load structure
    if structure_file.suffix.lower() == ".json":
        with open(structure_file, "r") as f:
            structure = Structure.from_dict(json.load(f))
    else:
        structure = Structure.from_file(str(structure_file))

    if store:
        # Run WorkChain
        inputs = {
            'structure': StructureData(pymatgen=structure),
            'sub_from': Str(sub_from),
            'sub_to': Str(sub_to),
            'concentrations': List(list=list(concentrations)),
            'max_size': Int(max_size),
            'max_steps': Int(max_steps),
            'symprec': Float(symprec),
        }
        result, node = run_get_node(SQSWorkChain, **inputs)
        click.echo(f"SQS generation complete. Results stored in node {node.pk}")
        # Save results to file
        # with open(output, "w") as f:
        #     json.dump(result['sqs_structures'].get_dict(), f, indent=2)
    else:
        # Run original function
        from .sqs import generate_sqs_structures
        _, result = generate_sqs_structures(
            structure_data=structure.as_dict(),
            sub_from=sub_from,
            sub_to=sub_to,
            concentrations=concentrations,
            max_size=max_size,
            max_steps=max_steps,
            symprec=symprec,
        )
        for conc_key, sqs_info in result.get("sqs_structures", {}).items():
            if "structure" in sqs_info:
                sqs_info["structure"] = sqs_info["structure"].as_dict()
        with open(output, "w") as f:
            json.dump(result, f, indent=2)


    # click.echo(f"SQS generation complete. Results saved to {output}")
