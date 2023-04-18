"""
Common transformations using ase.Atoms object
"""
from ase.build import sort as ase_sort
from ase.build.supercells import make_supercell as ase_supercell
import numpy as np

from aiida import orm
from aiida.engine import calcfunction


@calcfunction
def make_supercell(structure, supercell: list, **kwargs):
    """Make supercell structure, keep the tags in order"""

    tags = kwargs.get("tags", None)

    atoms = structure.get_ase()
    atoms.set_tags(tags)

    slist = supercell.get_list()
    if isinstance(slist[0], int):
        satoms = atoms.repeat(slist)
    else:
        satoms = ase_supercell(atoms, np.array(slist))
    if "no_sort" not in kwargs:
        satoms = ase_sort(satoms)

    if tags:
        stags = satoms.get_tags().tolist()
    satoms.set_tags(None)

    out = orm.StructureData(ase=satoms)
    out.label = structure.label + f" SUPER {slist[2]} {slist[2]} {slist[2]}"

    if tags:
        return {"structure": out, "tags": orm.List(list=stags)}
    return {"structure": out}
