---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python [conda env:aiida-2.0-dev]
  language: python
  name: python3
---

(tutorial-atomstracker)=
# Using AtomsTracker

Here we show how to use `AtomsTracker` to automatically record operations performed on `ase.Atoms`

+++

Installing AiiDA takes a few extra steps and require setting up an database normally (see [here](https://aiida.readthedocs.io/projects/aiida-core/en/latest/intro/get_started.html)).
Here, for demostration only, we use a temporay profile with `SqliteTempBackend`.

```{code-cell} ipython3
:tags: [hide-cell]

from aiida import load_profile, engine, orm, plugins
from aiida.manage.configuration import get_config
from aiida.storage.sqlite_temp import SqliteTempBackend

%load_ext aiida

profile = load_profile(
    SqliteTempBackend.create_profile(
        'myprofile',
        options={
            'warnings.development_version': False,
            'runner.poll.interval': 1
        },
        debug=False
    ),
    allow_switch=True
)
config = get_config()
config.add_profile(profile)
config.set_default_profile(profile.name)
profile
```

```{code-cell} ipython3
from aiida_atoms import AtomsTracker
from ase.build import bulk
```

The `ase.Atoms` object models a atomic structure can be used in various ways. It is the centre piece to the `ase` ecosystem and used for constructing structure, data analysis and also calculations themselves.
Here, we focus the first use case - using `ase.Atoms` for constructing input structures used in various materials modelling workflows.
A common pattern is to start from a bulk structure, constructed manually or loaded from a online database (such as ICSD), and perform certain operations before it is used as inputs for first-principles calculations.

In this example, we start with a bulk diamond structure and create defect supercell.
To load the diamond structure:

```{code-cell} ipython3
c2 = bulk("C")
```

Creating a supercell can be done with the `.repeat` method of a `ase.Atoms` object:

```{code-cell} ipython3
supercell = c2.repeat((3,3,3))
```

Note that `.repeat` is an out-of0place operation, e.g. a new `ase.Atoms` object is created

```{code-cell} ipython3
print(supercell)
```

A vacancy can be created by removing a single atom

```{code-cell} ipython3
supercell.pop(0)
print(supercell)
```

Now our supercell has only 53 atoms, we write it to the disk in the [POSCAR](https://www.vasp.at/wiki/index.php/POSCAR) format.

```{code-cell} ipython3
supercell.write("C_Vac_c.vasp")
```

The structure can be read into a different python session for further operation or used for calculation.

```{code-cell} ipython3
import ase.io
supercell_loaded = ase.io.read("C_Vac_c.vasp")
```

## Tracking operations performed on `ase.Atoms`

The file `C_Vac_c.vasp` itself does not contain any history about how it was made, e.g  which structure was used as the bulk and which atom was removed, especially with more complex structures.

Here comes the `AtomsTracker` to rescue! As the name suggests, it tracks the underlying `ase.Atoms` object as long as the methods called as those of the tracked object.

:::{seealso} Implementation
:class: dropdown

The tracker is implemented using the [@calcfunction](https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/calculations/concepts.html?#calculation-functions) api in AiiDA core.
The actual method calls `ase.Atoms` are done within a function wrapped by the `@calcfunction` decorator.
:::

```{code-cell} ipython3
tracker = AtomsTracker(c2)
tracker.label = "C2 Primitive"
defect_cell = tracker.repeat((3,3,3))
defect_cell.pop(0)
defect_cell.rattle(stdev=0.05, seed=11)
defect_cell.label = "C2 Rattled supercell"
```

now both `tracker` and `supercell` are `AtomsTracker` objects:

```{code-cell} ipython3
print(tracker)
print(defect_cell)
```

An `AtomsTracker` is just an `ase.Atoms` object plus an `aiida.orm.StructureData` with methods of `ase.Atoms` attached.

```{code-cell} ipython3
print(tracker.atoms)

print(tracker.node.__repr__())
```

```{code-cell} ipython3
print(defect_cell.atoms)

print(defect_cell.node.__repr__())
```

Now the `supercell` includes the history show how it was made

:::{danger}
Do not call the method of the underlying `ase.Atoms` object directly - this will cause the tracker to lose track of the atom, resulting in incorrect provenance.
:::


```{code-cell} ipython3
calc_pop = defect_cell.node.base.links.get_incoming().one()
print(calc_pop)
```

The [`LinkTriple`](https://aiida.readthedocs.io/projects/aiida-core/en/latest/howto/query.html?incoming-and-outgoing-links) object is an object to represent a link between two nodes. Here, one is the output strucutre `supercell.node` and the other is a `Calculation` that create the output.

We can also check what are the inputs used in this calculation:

```{code-cell} ipython3
calc_func = calc_pop.node
calc_func.base.links.get_incoming().all()
```

## Visualising provenance

AiiDA provides some tools to visualise the provenance.

```{code-cell} ipython3
from aiida.tools.visualization import Graph
def view_provenance(node, **kwargs):
    graph = Graph(graph_attr={"size":"7.0"})
    graph.recurse_ancestors(node, annotate_links="both")
    return graph.graphviz
def view_descendants(node, **kwargs):
    graph = Graph(graph_attr={"size":"7.0"})
    graph.recurse_descendants(node, annotate_links="both", include_process_inputs=True)
    return graph.graphviz
view_provenance(defect_cell.node)
```

:::{note}
You may will need to install `graphviz` to be able to render the graph in the notebook.

This can be down using `conda install -c conda-forge graphviz`.
:::

Great, we now have a full history of how our defect supercell is created.
`note`{The links are labeled with the names of the keyword arguments, but the positional arguments are labeld with *arg_00*.}

Now let'ts create a few more defect structures, note the `pop` operation does an in-place mutation of the `supercell`, hence we have lost access to our pristine supercell.
With the tracker, all intermediate results are stored in the database.
This allow us to load the pristine supercell back without problem.

```{code-cell} ipython3
perfect_supercell = AtomsTracker(orm.load_node(4))
defect2 = AtomsTracker(perfect_supercell)
defect2.pop(1)
```

Note that `.pop` returns an `ase.Atom` object, and the tracker retains this behaviour.

For out-of-place operations, such as `repeat` or `sort`, returns a tracker tracking the new `ase.Atoms` object created.

```{code-cell} ipython3
sorted_defect2 = defect2.sort()
sorted_defect2 is defect2
```

We can also check what the descendants of a given node are, as we used an bulk diamond structure as the starting point, all structures created are descendants of it.

```{code-cell} ipython3
view_descendants(tracker.node)
```

## Shortcuts

+++

The `AtomsTracker` also provides some shortcuts to the attributes of the underlying `StructureData` object.
The `AtomsTracker.base` is equivalent to `AtomsTracker.node.base`, for example

```{code-cell} ipython3
tracker.base.links.get_outgoing().all()
```

is the same as

```{code-cell} ipython3
tracker.node.base.links.get_outgoing().all()
```

The `label` and `descriptions` of the underlying `node` also have shortcut.

```{code-cell} ipython3
tracker.label = "My defect node"
tracker.description = "An initial C2 primitive cell"

print(tracker.node.label)
print(tracker.node.description)
```

## Using the data later

The `node` attribute of the tracker is stored in AiiDA's database. There are two ways to identify a `node`:

id
: An integer that is unique within the database, but may change is the data is exported and imported to other database afterwards.

uuid
: A long string that is unique and will remain constant when imported/exported.

The `uuid` is the preferred way of referring to the data as it is always stable.
Just like `label` and `description`, there are also shortcuts.

```{code-cell} ipython3
print(defect2.id)
print(defect2.uuid)
```

We can load the defect from the database again with, this works in a different python session as long as you have the correct `uuid`.

```{code-cell} ipython3
defect2_reloaded = AtomsTracker(orm.load_node(defect2.uuid))
defect2_reloaded
```

:::{tip}

One can also load data with first few characters of the `uuid` or the label of the node, as long as the value is unique in the database.

```python3
defect2_reloaded = AtomsTracker(orm.load_node("My defect node"))
```

should also work.
:::
