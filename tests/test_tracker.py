"""
Test the tracker
"""

from aiida_atoms.tracker import AseAtomsTracker
from ase.build import bulk

def check_atoms_equality(a1, a2, tol=1e-10):

    assert abs(a1.cell - a2.cell).max() < tol
    assert abs(a1.positions - a2.positions).max() < tol
    assert abs(a1.numbers == a2.numbers).all()

def test_tracker():
    """Test `AseAtomsTracker` type"""

    c2 = bulk("C")
    tracker = AseAtomsTracker(c2)
    supercell_tracked = tracker.repeat((2,2,2))
    displaced = tracker.translate([0, 0, 0.1])
    c2_displaced = c2.copy()
    c2_displaced.translate([0, 0, 0.1])

    supercell_atoms = c2.repeat((2,2,2))
    
    assert len(supercell_tracked.node.get_incoming().all()) == 1

    check_atoms_equality(supercell_atoms, supercell_tracked.atoms)
    check_atoms_equality(c2_displaced, displaced.atoms)

    mgo = bulk("MgO", "rocksalt", a=4.0)

    tracked_mgo = AseAtomsTracker(mgo)
    tracked_supercell = tracked_mgo.repeat((2,2,2))
    tracked_slice = tracked_supercell[:10]
    check_atoms_equality(tracked_slice.atoms, tracked_supercell.atoms[:10])

    