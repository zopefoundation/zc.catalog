##############################################################################
#
# Copyright (c) 2004 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""extent catalog

$Id: extentcatalog.py 3296 2005-09-09 19:29:20Z benji $
"""

from BTrees import IFBTree
import persistent
import persistent.dict
from zope import interface, component
from zope.app.catalog import catalog
from zope.app.intid.interfaces import IIntIds
from zope.app import zapi
import zope.app.component.hooks

from zc.catalog import interfaces

class FilterExtent(persistent.Persistent):
    interface.implements(interfaces.IFilterExtent)
    __parent__ = None

    def __init__(self, filter):
        self.set = IFBTree.IFTreeSet()
        self.filter = filter

    def addable(self, uid, obj):
        return self.filter(self, uid, obj)

    def clear(self):
        self.set.clear()

    def __or__(self, other):
        "extent | set"
        return self.union(other)

    __ror__ = __or__

    def union(self, other, self_weight=1, other_weight=1):
        return IFBTree.weightedUnion(
            self.set, other, self_weight, other_weight)[1]

    def __and__(self, other):
        "extent & set"
        return self.intersection(other)

    __rand__ = __and__

    def intersection(self, other, self_weight=1, other_weight=1):
        return IFBTree.weightedIntersection(
            self.set, other, self_weight, other_weight)[1]

    def __sub__(self, other):
        "extent - set"
        return self.difference(other)

    def difference(self, other):
        return IFBTree.difference(self.set, other)

    def __rsub__(self, other):
        "set - extent"
        return self.rdifference(other)

    def rdifference(self, other):
        return IFBTree.difference(other, self.set)

    def __iter__(self):
        return iter(self.set)

    def __nonzero__(self):
        return bool(self.set)

    def __contains__(self, uid):
        return self.set.has_key(uid)

    def add(self, uid, obj):
        if not self.addable(uid, obj):
            raise ValueError
        else:
            self.set.insert(uid)

    def remove(self, uid):
        self.set.remove(uid)

    def discard(self, uid):
        try:
            self.set.remove(uid)
        except KeyError:
            pass

UNINDEX = object()

class Catalog(catalog.Catalog):
    interface.implements(interfaces.IExtentCatalog)
    
    def __init__(self, extent):
        if extent.__parent__ is not None:
            raise ValueError("extent's __parent__ must be None")
        super(Catalog, self).__init__()
        self.extent = extent
        extent.__parent__ = self # inform extent of catalog
        self.queue = persistent.dict.PersistentDict()

    def clear(self):
        self.extent.clear()
        super(Catalog, self).clear()

    def _register(self):
        """Try to register to process queue later.

        Return whether we succeeded.
        """
        connection = self._p_jar
        if connection is None:
            return False

        try:
            tm = connection._txn_mgr
        except AttributeError:
            tm = connection.transaction_manager

        tm.get().addBeforeCommitHook(self._process)
        return True

    def _process(self):
        current_site = old_site = zope.app.component.hooks.getSite()
        try:
            for docid, (obj, site) in self.queue.items():
                if current_site is not site:
                    zope.app.component.hooks.setSite(site)
                    current_site = site
                if obj is not UNINDEX:
                    super(Catalog, self).index_doc(docid, obj)
                elif docid in self.extent:
                    super(Catalog, self).unindex_doc(docid)
                    self.extent.remove(docid)
            self.queue.clear()
        finally:
            zope.app.component.hooks.setSite(old_site)

    def index_doc(self, docid, texts):
        """Register the data in indexes of this catalog.
        """

        registered = True
        if not self.queue:
            registered = self._register()

        try:
            self.extent.add(docid, texts)
        except ValueError:
            #self.unindex_doc(docid)
            self.queue[docid] = (UNINDEX, zope.app.component.hooks.getSite())
        else:
            #super(Catalog, self).index_doc(docid, texts)
            self.queue[docid] = (texts, zope.app.component.hooks.getSite())

        if not registered:
            self._process()


    def unindex_doc(self, docid):
        """Unregister the data from indexes of this catalog."""

        registered = True
        if not self.queue:
            registered = self._register()

        self.queue[docid] = (UNINDEX, zope.app.component.hooks.getSite())

        if not registered:
            self._process()

    def updateIndex(self, index):
        if index.__parent__ is not self:
            # not an index in us.  Let the superclass handle it.
            super(Catalog, self).updateIndex(index)
        else:
            uidutil = zapi.getUtility(IIntIds)
            for uid in uidutil:
                obj = uidutil.getObject(uid)
                try:
                    self.extent.add(uid, obj)
                except ValueError:
                    self.unindex_doc(uid)
                else:
                    index.index_doc(uid, obj)

    def updateIndexes(self):
        uidutil = zapi.getUtility(IIntIds)
        for uid in uidutil:
            self.index_doc(uid, uidutil.getObject(uid))
