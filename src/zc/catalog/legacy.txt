=======================
Support for legacy data
=======================

Prior to the introduction of btree "families" and the
``BTrees.Interfaces.IBTreeFamily`` interface, the indexes defined by
the ``zc.catalog.index`` module used the instance attributes
``btreemodule`` and ``IOBTree``, initialized in the constructor, and
the ``BTreeAPI`` property.  These are replaced by the ``family``
attribute in the current implementation.

This is a white-box test that verifies that the supported values in
existing data structures (loaded from pickles) can be used effectively
with the current implementation.

There are two supported sets of values; one for 32-bit btrees::

  >>> import BTrees.IOBTree

  >>> legacy32 = {
  ...     "btreemodule": "BTrees.IFBTree",
  ...     "IOBTree": BTrees.IOBTree.IOBTree,
  ...     }

and another for 64-bit btrees::

  >>> import BTrees.LOBTree

  >>> legacy64 = {
  ...     "btreemodule": "BTrees.LFBTree",
  ...     "IOBTree": BTrees.LOBTree.LOBTree,
  ...     }

In each case, actual legacy structures will also include index
structures that match the right integer size::

  >>> import BTrees.OOBTree
  >>> import BTrees.Length

  >>> legacy32["values_to_documents"] = BTrees.OOBTree.OOBTree()
  >>> legacy32["documents_to_values"] = BTrees.IOBTree.IOBTree()
  >>> legacy32["documentCount"] = BTrees.Length.Length(0)
  >>> legacy32["wordCount"] = BTrees.Length.Length(0)

  >>> legacy64["values_to_documents"] = BTrees.OOBTree.OOBTree()
  >>> legacy64["documents_to_values"] = BTrees.LOBTree.LOBTree()
  >>> legacy64["documentCount"] = BTrees.Length.Length(0)
  >>> legacy64["wordCount"] = BTrees.Length.Length(0)

What we want to do is verify that the ``family`` attribute is properly
computed for instances loaded from legacy data, and ensure that the
structure is updated cleanly without providing cause for a read-only
transaction to become a write-transaction.  We'll need to create
instances that conform to the old data structures, pickle them, and
show that unpickling them produces instances that use the correct
families.

Let's create new instances, and force the internal data to match the
old structures::

  >>> import pickle
  >>> import zc.catalog.index

  >>> vi32 = zc.catalog.index.ValueIndex()
  >>> vi32.__dict__ = legacy32.copy()
  >>> legacy32_pickle = pickle.dumps(vi32)

  >>> vi64 = zc.catalog.index.ValueIndex()
  >>> vi64.__dict__ = legacy64.copy()
  >>> legacy64_pickle = pickle.dumps(vi64)

Now, let's unpickle these structures and verify the structures.  We'll
start with the 32-bit variety::

  >>> vi32 = pickle.loads(legacy32_pickle)

  >>> vi32.__dict__["btreemodule"]
  'BTrees.IFBTree'
  >>> vi32.__dict__["IOBTree"]
  <type 'BTrees.IOBTree.IOBTree'>

  >>> "family" in vi32.__dict__
  False

  >>> vi32._p_changed
  False

The ``family`` property returns the ``BTrees.family32`` singleton::

  >>> vi32.family is BTrees.family32
  True

Once accessed, the legacy values have been cleaned out from the
instance dictionary::

  >>> "btreemodule" in vi32.__dict__
  False
  >>> "IOBTree" in vi32.__dict__
  False
  >>> "BTreeAPI" in vi32.__dict__
  False

Accessing these attributes as attributes provides the proper values
anyway::

  >>> vi32.btreemodule
  'BTrees.IFBTree'
  >>> vi32.IOBTree
  <type 'BTrees.IOBTree.IOBTree'>
  >>> vi32.BTreeAPI
  <module 'BTrees.IFBTree' from ...>

Even though the instance dictionary has been cleaned up, the change
flag hasn't been set.  This is handled this way to avoid turning a
read-only transaction into a write-transaction::

  >>> vi32._p_changed
  False

The 64-bit variation provides equivalent behavior::

  >>> vi64 = pickle.loads(legacy64_pickle)

  >>> vi64.__dict__["btreemodule"]
  'BTrees.LFBTree'
  >>> vi64.__dict__["IOBTree"]
  <type 'BTrees.LOBTree.LOBTree'>

  >>> "family" in vi64.__dict__
  False

  >>> vi64._p_changed
  False

  >>> vi64.family is BTrees.family64
  True

  >>> "btreemodule" in vi64.__dict__
  False
  >>> "IOBTree" in vi64.__dict__
  False
  >>> "BTreeAPI" in vi64.__dict__
  False

  >>> vi64.btreemodule
  'BTrees.LFBTree'
  >>> vi64.IOBTree
  <type 'BTrees.LOBTree.LOBTree'>
  >>> vi64.BTreeAPI
  <module 'BTrees.LFBTree' from ...>

  >>> vi64._p_changed
  False

Now, if we have a legacy structure and explicitly set the ``family``
attribute, the old data structures will be cleared and replaced with
the new structure.  If the object is associated with a data manager,
the changed flag will be set as well::

  >>> class DataManager(object):
  ...     def register(self, ob):
  ...         pass

  >>> vi64 = pickle.loads(legacy64_pickle)
  >>> vi64._p_jar = DataManager()
  >>> vi64.family = BTrees.family64

  >>> vi64._p_changed
  True

  >>> "btreemodule" in vi64.__dict__
  False
  >>> "IOBTree" in vi64.__dict__
  False
  >>> "BTreeAPI" in vi64.__dict__
  False

  >>> "family" in vi64.__dict__
  True
  >>> vi64.family is BTrees.family64
  True

  >>> vi64.btreemodule
  'BTrees.LFBTree'
  >>> vi64.IOBTree
  <type 'BTrees.LOBTree.LOBTree'>
  >>> vi64.BTreeAPI
  <module 'BTrees.LFBTree' from ...>
