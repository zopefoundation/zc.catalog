================
 Extent Catalog
================

An extent catalog is very similar to a normal catalog except that it
only indexes items addable to its extent.  The extent is both a filter
and a set that may be merged with other result sets.  The filtering is
an additional feature we will discuss below; we'll begin with a simple
"do nothing" extent that only supports the second use case.

We create the state that the text needs here.

    >>> import zope.keyreference.persistent
    >>> import zope.component
    >>> import zope.intid
    >>> import zope.component
    >>> import zope.interface.interfaces
    >>> import zope.component.persistentregistry
    >>> from ZODB.MappingStorage import DB
    >>> import transaction

    >>> zope.component.provideAdapter(
    ...     zope.keyreference.persistent.KeyReferenceToPersistent,
    ...     adapts=(zope.interface.Interface,))
    >>> zope.component.provideAdapter(
    ...     zope.keyreference.persistent.connectionOfPersistent,
    ...     adapts=(zope.interface.Interface,))

    >>> site_manager = None
    >>> def getSiteManager(context=None):
    ...     if context is None:
    ...         if site_manager is None:
    ...             return zope.component.getGlobalSiteManager()
    ...         else:
    ...             return site_manager
    ...     else:
    ...         try:
    ...             return zope.interface.interfaces.IComponentLookup(context)
    ...         except TypeError as error:
    ...             raise zope.component.ComponentLookupError(*error.args)
    ...
    >>> def setSiteManager(sm):
    ...     global site_manager
    ...     site_manager = sm
    ...     if sm is None:
    ...         zope.component.getSiteManager.reset()
    ...     else:
    ...         zope.component.getSiteManager.sethook(getSiteManager)
    ...
    >>> def makeRoot():
    ...     db = DB()
    ...     conn = db.open()
    ...     root = conn.root()
    ...     site_manager = root['components'] = (
    ...         zope.component.persistentregistry.PersistentComponents())
    ...     site_manager.__bases__ = (zope.component.getGlobalSiteManager(),)
    ...     site_manager.registerUtility(
    ...         zope.intid.IntIds(family=btrees_family),
    ...         provided=zope.intid.interfaces.IIntIds)
    ...     setSiteManager(site_manager)
    ...     transaction.commit()
    ...     return root
    ...

    >>> @zope.component.adapter(zope.interface.Interface)
    ... @zope.interface.implementer(zope.interface.interfaces.IComponentLookup)
    ... def getComponentLookup(obj):
    ...     return obj._p_jar.root()['components']
    ...
    >>> zope.component.provideAdapter(getComponentLookup)

To show the extent catalog at work, we need an intid utility, an
index, some items to index.  We'll do this within a real ZODB and a
real intid utility.

    >>> import zc.catalog
    >>> import zc.catalog.interfaces
    >>> from zc.catalog import interfaces, extentcatalog
    >>> from zope import interface, component
    >>> from zope.interface import verify
    >>> import persistent
    >>> import BTrees.IFBTree

    >>> root = makeRoot()
    >>> intid = zope.component.getUtility(
    ...     zope.intid.interfaces.IIntIds, context=root)
    >>> TreeSet = btrees_family.IF.TreeSet

    >>> from zope.container.interfaces import IContained
    >>> @interface.implementer(IContained)
    ... class DummyIndex(persistent.Persistent):
    ...     __parent__ = __name__ = None
    ...     def __init__(self):
    ...         self.uids = TreeSet()
    ...     def unindex_doc(self, uid):
    ...         if uid in self.uids:
    ...             self.uids.remove(uid)
    ...     def index_doc(self, uid, obj):
    ...         self.uids.insert(uid)
    ...     def clear(self):
    ...         self.uids.clear()
    ...     def apply(self, query):
    ...         return [uid for uid in self.uids if uid <= query]
    ...
    >>> class DummyContent(persistent.Persistent):
    ...     def __init__(self, name, parent):
    ...         self.id = name
    ...         self.__parent__ = parent
    ...

    >>> extent = extentcatalog.Extent(family=btrees_family)
    >>> verify.verifyObject(interfaces.IExtent, extent)
    True
    >>> root['catalog'] = catalog = extentcatalog.Catalog(extent)
    >>> verify.verifyObject(interfaces.IExtentCatalog, catalog)
    True
    >>> index = DummyIndex()
    >>> catalog['index'] = index
    >>> transaction.commit()

Now we have a catalog set up with an index and an extent.  We can add
some data to the extent:

    >>> matches = []
    >>> for i in range(100):
    ...     c = DummyContent(i, root)
    ...     root[i] = c
    ...     doc_id = intid.register(c)
    ...     catalog.index_doc(doc_id, c)
    ...     matches.append(doc_id)
    >>> matches.sort()
    >>> sorted(extent) == sorted(index.uids) == matches
    True

We can get the size of the extent.

    >>> len(extent)
    100

Unindexing an object that is in the catalog should simply remove it from the
catalog and index as usual.

    >>> matches[0] in catalog.extent
    True
    >>> matches[0] in catalog['index'].uids
    True
    >>> catalog.unindex_doc(matches[0])
    >>> matches[0] in catalog.extent
    False
    >>> matches[0] in catalog['index'].uids
    False
    >>> doc_id = matches.pop(0)
    >>> sorted(extent) == sorted(index.uids) == matches
    True

Clearing the catalog clears both the extent and the contained indexes.

    >>> catalog.clear()
    >>> list(catalog.extent) == list(catalog['index'].uids) == []
    True

Updating all indexes and an individual index both also update the extent.

    >>> catalog.updateIndexes()
    >>> matches.insert(0, doc_id)
    >>> sorted(extent) == sorted(index.uids) == matches
    True

    >>> index2 = DummyIndex()
    >>> catalog['index2'] = index2
    >>> index2.__parent__ == catalog
    True
    >>> index.uids.remove(matches[0]) # to confirm that only index 2 is touched
    >>> catalog.updateIndex(index2)
    >>> sorted(extent) == sorted(index2.uids) == matches
    True
    >>> matches[0] in index.uids
    False
    >>> matches[0] in index2.uids
    True
    >>> res = index.uids.insert(matches[0])

But so why have an extent in the first place?  It allows indices to
operate against a reliable collection of the full indexed data;
therefore, it allows the indices in zc.catalog to perform NOT
operations.

The extent itself provides a number of merging features to allow its
values to be merged with other BTrees.IFBTree data structures.  These
include intersection, union, difference, and reverse difference.
Given an extent named 'extent' and another IFBTree data structure
named 'data', intersections can be spelled "extent & data" or "data &
extent"; unions can be spelled "extent | data" or "data | extent";
differences can be spelled "extent - data"; and reverse differences
can be spelled "data - extent".  Unions and intersections are
weighted.

    >>> extent = extentcatalog.Extent(family=btrees_family)
    >>> for i in range(1, 100, 2):
    ...     extent.add(i, None)
    ...
    >>> alt_set = TreeSet()
    >>> _ = alt_set.update(range(0, 166, 33)) # return value is unimportant here
    >>> sorted(alt_set)
    [0, 33, 66, 99, 132, 165]
    >>> sorted(extent & alt_set)
    [33, 99]
    >>> sorted(alt_set & extent)
    [33, 99]
    >>> sorted(extent.intersection(alt_set))
    [33, 99]
    >>> original = set(extent)
    >>> union_matches = original.copy()
    >>> union_matches.update(alt_set)
    >>> union_matches = sorted(union_matches)
    >>> sorted(alt_set | extent) == union_matches
    True
    >>> sorted(extent | alt_set) == union_matches
    True
    >>> sorted(extent.union(alt_set)) == union_matches
    True
    >>> sorted(alt_set - extent)
    [0, 66, 132, 165]
    >>> sorted(extent.rdifference(alt_set))
    [0, 66, 132, 165]
    >>> original.remove(33)
    >>> original.remove(99)
    >>> set(extent - alt_set) == original
    True
    >>> set(extent.difference(alt_set)) == original
    True

We can pass our own instantiated UID utility to extentcatalog.Catalog.

    >>> extent = extentcatalog.Extent(family=btrees_family)
    >>> uidutil = zope.intid.IntIds()
    >>> cat = extentcatalog.Catalog(extent, uidutil)
    >>> cat["index"] = DummyIndex()
    >>> cat.UIDSource is uidutil
    True

    >>> cat._getUIDSource() is uidutil
    True

The ResultSet instance returned by the catalog's `searchResults` method
uses our UID utility.

    >>> obj = DummyContent(43, root)
    >>> uid = uidutil.register(obj)
    >>> cat.index_doc(uid, obj)
    >>> res = cat.searchResults(index=uid)
    >>> res.uidutil is uidutil
    True

    >>> list(res) == [obj]
    True

`searchResults` may also return None.

    >>> cat.searchResults() is None
    True

Calling `updateIndex` and `updateIndexes` when the catalog has its uid source
set works as well.

    >>> cat.clear()
    >>> uid in cat.extent
    False

All objects in the uid utility are indexed.

    >>> cat.updateIndexes()
    >>> uid in cat.extent
    True

    >>> len(cat.extent)
    1

    >>> obj2 = DummyContent(44, root)
    >>> uid2 = uidutil.register(obj2)
    >>> cat.updateIndexes()
    >>> len(cat.extent)
    2

    >>> uid2 in cat.extent
    True

    >>> uidutil.unregister(obj2)

    >>> cat.clear()
    >>> uid in cat.extent
    False
    >>> cat.updateIndex(cat["index"])
    >>> uid in cat.extent
    True

With a self-populating extent, calling `updateIndex` or `updateIndexes` means
only the objects whose ids are in the extent are updated/reindexed; if present,
the catalog will use its uid source to look up the objects by id.

    >>> extent = extentcatalog.NonPopulatingExtent(family=btrees_family)
    >>> cat = extentcatalog.Catalog(extent, uidutil)
    >>> cat["index"] = DummyIndex()

    >>> extent.add(uid, obj)
    >>> uid in cat["index"].uids
    False

    >>> cat.updateIndexes()
    >>> uid in cat["index"].uids
    True

    >>> cat.clear()
    >>> uid in cat["index"].uids
    False

    >>> uid in cat.extent
    False

    >>> cat.extent.add(uid, obj)
    >>> cat.updateIndex(cat["index"])
    >>> uid in cat["index"].uids
    True

Unregister the objects of the previous tests from intid utility:

    >>> intid = zope.component.getUtility(
    ...     zope.intid.interfaces.IIntIds, context=root)
    >>> for doc_id in matches:
    ...     intid.unregister(intid.queryObject(doc_id))


Catalog with a filter extent
============================

As discussed at the beginning of this document, extents can not only help
with index operations, but also act as a filter, so that a given catalog
can answer questions about a subset of the objects contained in the intids.

The filter extent only stores objects that match a given filter.

    >>> def filter(extent, uid, ob):
    ...     assert interfaces.IFilterExtent.providedBy(extent)
    ...     # This is an extent of objects with odd-numbered uids without a
    ...     # True ignore attribute
    ...     return uid % 2 and not getattr(ob, 'ignore', False)
    ...
    >>> extent = extentcatalog.FilterExtent(filter, family=btrees_family)
    >>> verify.verifyObject(interfaces.IFilterExtent, extent)
    True
    >>> root['catalog1'] = catalog = extentcatalog.Catalog(extent)
    >>> verify.verifyObject(interfaces.IExtentCatalog, catalog)
    True
    >>> index = DummyIndex()
    >>> catalog['index'] = index
    >>> transaction.commit()

Now we have a catalog set up with an index and an extent.  If we create
some content and ask the catalog to index it, only the ones that match
the filter will be in the extent and in the index.

    >>> matches = []
    >>> fails = []
    >>> i = 0
    >>> while True:
    ...     c = DummyContent(i, root)
    ...     root[i] = c
    ...     doc_id = intid.register(c)
    ...     catalog.index_doc(doc_id, c)
    ...     if filter(extent, doc_id, c):
    ...         matches.append(doc_id)
    ...     else:
    ...         fails.append(doc_id)
    ...     i += 1
    ...     if i > 99 and len(matches) > 4:
    ...         break
    ...
    >>> matches.sort()
    >>> sorted(extent) == sorted(index.uids) == matches
    True

If a content object is indexed that used to match the filter but no longer
does, it should be removed from the extent and indexes.

    >>> matches[0] in catalog.extent
    True
    >>> obj = intid.getObject(matches[0])
    >>> obj.ignore = True
    >>> filter(extent, matches[0], obj)
    False
    >>> catalog.index_doc(matches[0], obj)
    >>> doc_id = matches.pop(0)
    >>> doc_id in catalog.extent
    False
    >>> sorted(extent) == sorted(index.uids) == matches
    True

Unindexing an object that is not in the catalog should be a no-op.

    >>> fails[0] in catalog.extent
    False
    >>> catalog.unindex_doc(fails[0])
    >>> fails[0] in catalog.extent
    False
    >>> sorted(extent) == sorted(index.uids) == matches
    True

Updating all indexes and an individual index both also update the extent.

    >>> index2 = DummyIndex()
    >>> catalog['index2'] = index2
    >>> index2.__parent__ == catalog
    True
    >>> index.uids.remove(matches[0]) # to confirm that only index 2 is touched
    >>> catalog.updateIndex(index2)
    >>> sorted(extent) == sorted(index2.uids)
    True
    >>> matches[0] in index.uids
    False
    >>> matches[0] in index2.uids
    True
    >>> res = index.uids.insert(matches[0])

If you update a single index and an object is no longer a member of the extent,
it is removed from all indexes.

    >>> matches[0] in catalog.extent
    True
    >>> matches[0] in index.uids
    True
    >>> matches[0] in index2.uids
    True
    >>> obj = intid.getObject(matches[0])
    >>> obj.ignore = True
    >>> catalog.updateIndex(index2)
    >>> matches[0] in catalog.extent
    False
    >>> matches[0] in index.uids
    False
    >>> matches[0] in index2.uids
    False
    >>> doc_id = matches.pop(0)
    >>> (matches == sorted(catalog.extent) == sorted(index.uids)
    ...  == sorted(index2.uids))
    True


Self-populating extents
=======================

An extent may know how to populate itself; this is especially useful if
the catalog can be initialized with fewer items than those available in
the IIntIds utility that are also within the nearest Zope 3 site (the
policy coded in the basic Zope 3 catalog).

Such an extent must implement the `ISelfPopulatingExtent` interface,
which requires two attributes.  Let's use the `FilterExtent` class as a
base for implementing such an extent, with a method that selects content item
0 (created and registered above)::

    >>> class PopulatingExtent(
    ...     extentcatalog.FilterExtent,
    ...     extentcatalog.NonPopulatingExtent):
    ...
    ...     def populate(self):
    ...         if self.populated:
    ...             return
    ...         self.add(intid.getId(root[0]), root[0])
    ...         super(PopulatingExtent, self).populate()

Creating a catalog based on this extent ignores objects in the
database already::

    >>> def accept_any(extent, uid, ob):
    ...     return True

    >>> extent = PopulatingExtent(accept_any, family=btrees_family)
    >>> catalog = extentcatalog.Catalog(extent)
    >>> index = DummyIndex()
    >>> catalog['index'] = index
    >>> root['catalog2'] = catalog
    >>> transaction.commit()

At this point, our extent remains unpopulated::

    >>> extent.populated
    False

Iterating over the extent does not cause it to be automatically
populated::

    >>> list(extent)
    []

Causing our new index to be filled will cause the `populate()` method
to be called, setting the `populate` flag as a side-effect::

    >>> catalog.updateIndex(index)
    >>> extent.populated
    True

    >>> list(extent) == [intid.getId(root[0])]
    True

The index has been updated with the documents identified by the
extent::

    >>> list(index.uids) == [intid.getId(root[0])]
    True

Updating the same index repeatedly will continue to use the extent as
the source of documents to include::

    >>> catalog.updateIndex(index)

    >>> list(extent) == [intid.getId(root[0])]
    True
    >>> list(index.uids) == [intid.getId(root[0])]
    True

The `updateIndexes()` method has a similar behavior.  If we add an
additional index to the catalog, we see that it indexes only those
objects from the extent::

    >>> index2 = DummyIndex()
    >>> catalog['index2'] = index2

    >>> catalog.updateIndexes()

    >>> list(extent) == [intid.getId(root[0])]
    True
    >>> list(index.uids) == [intid.getId(root[0])]
    True
    >>> list(index2.uids) == [intid.getId(root[0])]
    True

When we have fresh catalog and extent (not yet populated), we see that
`updateIndexes()` will cause the extent to be populated::

    >>> extent = PopulatingExtent(accept_any, family=btrees_family)
    >>> root['catalog3'] = catalog = extentcatalog.Catalog(extent)
    >>> index1 = DummyIndex()
    >>> index2 = DummyIndex()
    >>> catalog['index1'] = index1
    >>> catalog['index2'] = index2
    >>> transaction.commit()

    >>> extent.populated
    False

    >>> catalog.updateIndexes()

    >>> extent.populated
    True

    >>> list(extent) == [intid.getId(root[0])]
    True
    >>> list(index1.uids) == [intid.getId(root[0])]
    True
    >>> list(index2.uids) == [intid.getId(root[0])]
    True

We'll make sure everything can be safely committed.

    >>> transaction.commit()
    >>> setSiteManager(None)
