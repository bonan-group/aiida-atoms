# Getting started

## Installation

Use the following commands to install the plugin:

```
git clone https://github.com/zhubonan/aiida-atoms .
cd aiida-atoms
pip install -e .  # also installs aiida, if missing (but not postgres)
```

## Usage

A quick demo of how to use the plugin:

```python
from aiida_atoms import AtomsTracker
from ase.build import bulk
from aiida.orm import load_profile

load_profile()

mgo = bulk("MgO", "rocksalt", 4.0)

# Directing acting on Atoms object without tracking
mgo = mgo.repeat((2,2,2))
mgo.translate((0.,0.,1))
mgo.pop(0)

# With tracker
mgo = AtomsTracker(bulk("MgO", "rocksalt", 4.0))
mgo.node  # Underlying orm.StructureData object

mgo = mgo.repeat((2,2,2))  # Create a new object
mgo.translate((0.,0.,1))
mgo.pop(0)

# History of the operations are stored in the provenance graph

q = QueryBuilder()
q.append(orm.Node, filters={'id':mgo.node.id}, tag='root')
q.append(orm.Node, with_descendants='root')
# Show all ancestor nodes of the final structure
q.all()
```

Make sure you checkout this [tutorial](tracking-example).
