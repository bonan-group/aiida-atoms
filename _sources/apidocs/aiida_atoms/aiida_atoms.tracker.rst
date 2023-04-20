:py:mod:`aiida_atoms.tracker`
=============================

.. py:module:: aiida_atoms.tracker

.. autodoc2-docstring:: aiida_atoms.tracker
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`AtomsTracker <aiida_atoms.tracker.AtomsTracker>`
     - .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`dummy_function <aiida_atoms.tracker.dummy_function>`
     - .. autodoc2-docstring:: aiida_atoms.tracker.dummy_function
          :summary:
   * - :py:obj:`wraps_ase_out_of_place <aiida_atoms.tracker.wraps_ase_out_of_place>`
     - .. autodoc2-docstring:: aiida_atoms.tracker.wraps_ase_out_of_place
          :summary:
   * - :py:obj:`wraps_ase_inplace <aiida_atoms.tracker.wraps_ase_inplace>`
     - .. autodoc2-docstring:: aiida_atoms.tracker.wraps_ase_inplace
          :summary:
   * - :py:obj:`to_aiida_rep <aiida_atoms.tracker.to_aiida_rep>`
     - .. autodoc2-docstring:: aiida_atoms.tracker.to_aiida_rep
          :summary:
   * - :py:obj:`_populate_methods <aiida_atoms.tracker._populate_methods>`
     - .. autodoc2-docstring:: aiida_atoms.tracker._populate_methods
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`wop <aiida_atoms.tracker.wop>`
     - .. autodoc2-docstring:: aiida_atoms.tracker.wop
          :summary:

API
~~~

.. py:function:: dummy_function(*args, **kwargs)
   :canonical: aiida_atoms.tracker.dummy_function

   .. autodoc2-docstring:: aiida_atoms.tracker.dummy_function

.. py:function:: wraps_ase_out_of_place(func)
   :canonical: aiida_atoms.tracker.wraps_ase_out_of_place

   .. autodoc2-docstring:: aiida_atoms.tracker.wraps_ase_out_of_place

.. py:data:: wop
   :canonical: aiida_atoms.tracker.wop
   :value: None

   .. autodoc2-docstring:: aiida_atoms.tracker.wop

.. py:function:: wraps_ase_inplace(func)
   :canonical: aiida_atoms.tracker.wraps_ase_inplace

   .. autodoc2-docstring:: aiida_atoms.tracker.wraps_ase_inplace

.. py:function:: to_aiida_rep(pobj)
   :canonical: aiida_atoms.tracker.to_aiida_rep

   .. autodoc2-docstring:: aiida_atoms.tracker.to_aiida_rep

.. py:class:: AtomsTracker(obj, atoms: typing.Union[ase.Atoms, None] = None, track=True)
   :canonical: aiida_atoms.tracker.AtomsTracker

   .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker

   .. rubric:: Initialization

   .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker.__init__

   .. py:method:: __repr__() -> str
      :canonical: aiida_atoms.tracker.AtomsTracker.__repr__

      .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker.__repr__

   .. py:attribute:: sort
      :canonical: aiida_atoms.tracker.AtomsTracker.sort
      :value: None

      .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker.sort

   .. py:attribute:: make_supercell
      :canonical: aiida_atoms.tracker.AtomsTracker.make_supercell
      :value: None

      .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker.make_supercell

   .. py:property:: label
      :canonical: aiida_atoms.tracker.AtomsTracker.label

      .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker.label

   .. py:property:: description
      :canonical: aiida_atoms.tracker.AtomsTracker.description

      .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker.description

   .. py:property:: id
      :canonical: aiida_atoms.tracker.AtomsTracker.id

      .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker.id

   .. py:property:: uuid
      :canonical: aiida_atoms.tracker.AtomsTracker.uuid

      .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker.uuid

   .. py:property:: base
      :canonical: aiida_atoms.tracker.AtomsTracker.base

      .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker.base

   .. py:method:: store_node(*args, **kwargs)
      :canonical: aiida_atoms.tracker.AtomsTracker.store_node

      .. autodoc2-docstring:: aiida_atoms.tracker.AtomsTracker.store_node

.. py:function:: _populate_methods()
   :canonical: aiida_atoms.tracker._populate_methods

   .. autodoc2-docstring:: aiida_atoms.tracker._populate_methods
