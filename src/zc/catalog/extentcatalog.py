#############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
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
from zope import interface, component
from zope.app.catalog import catalog
from zope.app.intid.interfaces import IIntIds
import zope.component

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

class Catalog(catalog.Catalog):
    interface.implements(interfaces.IExtentCatalog)
    
    def __init__(self, extent):
        if extent.__parent__ is not None:
            raise ValueError("extent's __parent__ must be None")
        super(Catalog, self).__init__()
        self.extent = extent
        extent.__parent__ = self # inform extent of catalog

    def clear(self):
        self.extent.clear()
        super(Catalog, self).clear()

    def index_doc(self, docid, texts):
        """Register the data in indexes of this catalog.
        """
        try:
            self.extent.add(docid, texts)
        except ValueError:
            self.unindex_doc(docid)
        else:
            super(Catalog, self).index_doc(docid, texts)

    def unindex_doc(self, docid):
        if docid in self.extent:
            super(Catalog, self).unindex_doc(docid)
            self.extent.remove(docid)

    def updateIndex(self, index):
        if index.__parent__ is not self:
            # not an index in us.  Let the superclass handle it.
            super(Catalog, self).updateIndex(index)
        else:
            uidutil = zope.component.getUtility(IIntIds)

            if interfaces.ISelfPopulatingExtent.providedBy(self.extent):
                if not self.extent.populated:
                    self.extent.populate()
                    assert self.extent.populated

                for uid in self.extent:
                    obj = uidutil.getObject(uid)
                    index.index_doc(uid, obj)

            else:
                for uid in uidutil:
                    obj = uidutil.getObject(uid)
                    try:
                        self.extent.add(uid, obj)
                    except ValueError:
                        self.unindex_doc(uid)
                    else:
                        index.index_doc(uid, obj)

    def updateIndexes(self):
        uidutil = zope.component.getUtility(IIntIds)

        if interfaces.ISelfPopulatingExtent.providedBy(self.extent):
            if not self.extent.populated:
                self.extent.populate()
                assert self.extent.populated

            for uid in self.extent:
                self.index_doc(uid, uidutil.getObject(uid))

        else:
            for uid in uidutil:
                self.index_doc(uid, uidutil.getObject(uid))
