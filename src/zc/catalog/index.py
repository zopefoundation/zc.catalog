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
"""indexes, as might be found in zope.index

"""
import sys
import datetime
import pytz.reference
import BTrees
import persistent
from BTrees import Length
from BTrees.Interfaces import IMerge

from zope import component, interface
import zope.component.interfaces
import zope.interface.common.idatetime
import zope.index.interfaces
from zope.index.field.sorting import SortingIndexMixin
import zope.security.management
from zope.publisher.interfaces import IRequest
import zc.catalog.interfaces
from zc.catalog.i18n import _


class FamilyProperty(object):

    __name__ = "family"

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        d = instance.__dict__
        if "family" in d:
            return d["family"]

        if "btreemodule" in d:
            iftype = d["btreemodule"].split(".")[-1][:2]
            if iftype == "IF":
                d["family"] = BTrees.family32
            elif iftype == "LF":
                d["family"] = BTrees.family64
            else: # pragma: no cover
                raise ValueError("can't determine btree family based on"
                                 " btreemodule of %r" % (iftype,))
        else:
            d["family"] = BTrees.family32
        self._clear_old_cruft(instance)

        if isinstance(instance, persistent.Persistent):
            # Mutating the dict directly is not guaranteed to
            # register with the data manager.
            instance._p_changed = True

        return d["family"]

    def __set__(self, instance, value):
        instance.__dict__["family"] = value
        self._clear_old_cruft(instance)
        if isinstance(instance, persistent.Persistent):
            # Mutating the dict directly is not guaranteed to
            # register with the data manager.
            instance._p_changed = True

    def _clear_old_cruft(self, instance):
        d = instance.__dict__
        if "btreemodule" in d:
            del d["btreemodule"]
        if "IOBTree" in d:
            del d["IOBTree"]
        if "BTreeAPI" in d:
            del d["BTreeAPI"]



@interface.implementer(
    zope.index.interfaces.IInjection,
    zope.index.interfaces.IIndexSearch,
    zope.index.interfaces.IStatistics,
    zc.catalog.interfaces.IIndexValues,
)
class AbstractIndex(persistent.Persistent):


    family = FamilyProperty()

    def __init__(self, family=None):
        if family is not None:
            self.family = family
        self.clear()

    # These three are deprecated (they were never interface), but can
    # all be computed from the family attribute:

    @property
    def btreemodule(self):
        return self.family.IF.__name__

    @property
    def BTreeAPI(self):
        return self.family.IF

    @property
    def IOBTree(self):
        return self.family.IO.BTree

    def clear(self):
        self.values_to_documents = self.family.OO.BTree()
        self.documents_to_values = self.family.IO.BTree()
        self.documentCount = Length.Length(0)
        self.wordCount = Length.Length(0)

    def minValue(self, min=None):
        if min is None:
            return self.values_to_documents.minKey()
        else:
            return self.values_to_documents.minKey(min)

    def maxValue(self, max=None):
        if max is None:
            return self.values_to_documents.maxKey()
        else:
            return self.values_to_documents.maxKey(max)

    def values(self, min=None, max=None, excludemin=False, excludemax=False,
               doc_id=None):
        if doc_id is None:
            return iter(self.values_to_documents.keys(
                min, max, excludemin, excludemax))
        else:
            values = self.documents_to_values.get(doc_id)
            if values is None:
                return ()
            else:
                return iter(values.keys(min, max, excludemin, excludemax))

    def containsValue(self, value):
        try:
            return bool(self.values_to_documents.has_key(value))
        except TypeError:
            return False

    def ids(self):
        return self.documents_to_values.keys()

def parseQuery(query):
    if not isinstance(query, dict): # pragma: no cover
        raise ValueError('may only pass a dict to apply')

    if len(query) > 1:
        raise ValueError(
            'may only pass one of key, value pair')
    elif not query:
        return None, None
    query_type, query = list(query.items())[0]
    query_type = query_type.lower()
    return query_type, query


@interface.implementer(zc.catalog.interfaces.IValueIndex)
class ValueIndex(SortingIndexMixin, AbstractIndex):


    # attributes used by sorting mixin
    _sorting_num_docs_attr = 'documentCount'        # Length object
    _sorting_fwd_index_attr = 'values_to_documents' # forward BTree index
    _sorting_rev_index_attr = 'documents_to_values' # reverse BTree index

    def _add_value(self, doc_id, added):
        values_to_documents = self.values_to_documents
        docs = values_to_documents.get(added)
        if docs is None:
            values_to_documents[added] = self.family.IF.TreeSet((doc_id,))
            self.wordCount.change(1)
        else:
            docs.insert(doc_id)

    def index_doc(self, doc_id, value):
        if value is None:
            self.unindex_doc(doc_id)
        else:
            values_to_documents = self.values_to_documents
            documents_to_values = self.documents_to_values
            old = documents_to_values.get(doc_id)
            documents_to_values[doc_id] = value
            if old is None:
                self.documentCount.change(1)
            elif old != value:
                docs = values_to_documents.get(old)
                docs.remove(doc_id)
                if not docs:
                    del values_to_documents[old]
                    self.wordCount.change(-1)
            self._add_value(doc_id, value)

    def unindex_doc(self, doc_id):
        documents_to_values = self.documents_to_values
        value = documents_to_values.get(doc_id)
        if value is not None:
            values_to_documents = self.values_to_documents
            self.documentCount.change(-1)
            del documents_to_values[doc_id]
            docs = values_to_documents.get(value)
            docs.remove(doc_id)
            if not docs:
                del values_to_documents[value]
                self.wordCount.change(-1)

    def apply(self, query): # any_of, any, between, none,
        values_to_documents = self.values_to_documents
        query_type, query = parseQuery(query)
        if query_type is None:
            res = None
        elif query_type == 'any_of':
            try:
                res = self.family.IF.multiunion(
                    [s for s in (values_to_documents.get(v) for v in query)
                     if s is not None])
            except TypeError:
                return []
        elif query_type == 'any':
            if query is None:
                res = self.family.IF.Set(self.ids())
            else:
                assert zc.catalog.interfaces.IExtent.providedBy(query)
                res = query & self.family.IF.Set(self.ids())
        elif query_type == 'between':
            try:
                res = self.family.IF.multiunion(
                    [s for s in (values_to_documents.get(v) for v in
                                 values_to_documents.keys(*query))
                     if s is not None])
            except TypeError:
                return []
        elif query_type == 'none':
            assert zc.catalog.interfaces.IExtent.providedBy(query)
            res = query - self.family.IF.Set(self.ids())
        else:
            raise ValueError(
                "unknown query type", query_type)
        return res

    def values(self, min=None, max=None, excludemin=False, excludemax=False,
               doc_id=None):
        if doc_id is None:
            return iter(self.values_to_documents.keys(
                min, max, excludemin, excludemax))
        else:
            value = self.documents_to_values.get(doc_id)
            if (value is None or
                min is not None and (
                    value < min or excludemin and value == min) or
                max is not None and (
                    value > max or excludemax and value == max)):
                return ()
            else:
                return (value,)


@interface.implementer(zc.catalog.interfaces.ISetIndex)
class SetIndex(AbstractIndex):

    def _add_values(self, doc_id, added):
        values_to_documents = self.values_to_documents
        for v in added:
            docs = values_to_documents.get(v)
            if docs is None:
                values_to_documents[v] = self.family.IF.TreeSet((doc_id,))
                self.wordCount.change(1)
            else:
                docs.insert(doc_id)

    def index_doc(self, doc_id, value):
        new = self.family.OO.TreeSet(v for v in value if v is not None)
        if not new:
            self.unindex_doc(doc_id)
        else:
            values_to_documents = self.values_to_documents
            documents_to_values = self.documents_to_values
            old = documents_to_values.get(doc_id)
            if old is None:
                documents_to_values[doc_id] = new
                self.documentCount.change(1)
                self._add_values(doc_id, new)
            else:
                removed = self.family.OO.difference(old, new)
                added = self.family.OO.difference(new, old)
                for v in removed:
                    old.remove(v)
                    docs = values_to_documents.get(v)
                    docs.remove(doc_id)
                    if not docs:
                        del values_to_documents[v]
                        self.wordCount.change(-1)
                old.update(added)
                self._add_values(doc_id, added)

    def unindex_doc(self, doc_id):
        documents_to_values = self.documents_to_values
        values = documents_to_values.get(doc_id)
        if values is not None:
            values_to_documents = self.values_to_documents
            self.documentCount.change(-1)
            del documents_to_values[doc_id]
            for v in values:
                docs = values_to_documents.get(v)
                docs.remove(doc_id)
                if not docs:
                    del values_to_documents[v]
                    self.wordCount.change(-1)

    def apply(self, query): # any_of, any, between, none, all_of
        values_to_documents = self.values_to_documents
        query_type, query = parseQuery(query)
        if query_type is None:
            res = None
        elif query_type == 'any_of':
            res = self.family.IF.Bucket()
            for v in query:
                try:
                    _, res = self.family.IF.weightedUnion(
                        res, values_to_documents.get(v))
                except TypeError:
                    continue
        elif query_type == 'any':
            if query is None:
                res = self.family.IF.Set(self.ids())
            else:
                assert zc.catalog.interfaces.IExtent.providedBy(query)
                res = query & self.family.IF.Set(self.ids())
        elif query_type == 'all_of':
            res = None
            values = iter(query)
            empty = self.family.IF.TreeSet()
            try:
                res = values_to_documents.get(next(values), empty)
            except StopIteration:
                res = empty
            except TypeError:
                return []

            while res:
                try:
                    v = next(values)
                except StopIteration:
                    break
                try:
                    res = self.family.IF.intersection(
                        res, values_to_documents.get(v, empty))
                except TypeError:
                    return []
        elif query_type == 'between':
            res = self.family.IF.Bucket()
            try:
                for v in values_to_documents.keys(*query):
                    _, res = self.family.IF.weightedUnion(
                        res, values_to_documents.get(v))
            except TypeError:
                return []
        elif query_type == 'none':
            assert zc.catalog.interfaces.IExtent.providedBy(query)
            res = query - self.family.IF.Set(self.ids())
        else:
            raise ValueError(
                "unknown query type", query_type)
        return res


@interface.implementer(zc.catalog.interfaces.INormalizationWrapper)
class NormalizationWrapper(persistent.Persistent):

    index = normalizer = None
    collection_index = False

    def documentCount(self):
        return self.index.documentCount()

    def wordCount(self):
        return self.index.wordCount()

    def clear(self):
        """see zope.index.interfaces.IInjection.clear"""
        return self.index.clear()

    def __init__(self, index, normalizer, collection_index=False):
        self.index = index
        if zope.index.interfaces.IIndexSort.providedBy(index):
            zope.interface.alsoProvides(self, zope.index.interfaces.IIndexSort)
        self.normalizer = normalizer
        self.collection_index = collection_index

    def index_doc(self, doc_id, value):
        if self.collection_index:
            self.index.index_doc(
                doc_id, (self.normalizer.value(v) for v in value))
        else:
            self.index.index_doc(doc_id, self.normalizer.value(value))

    def unindex_doc(self, doc_id):
        self.index.unindex_doc(doc_id)

    def apply(self, query):
        query_type, query = parseQuery(query)
        if query_type == 'any_of':
            res = set()
            for v in query:
                res.update(self.normalizer.any(v, self.index))
        elif query_type == 'all_of':
            res = [self.normalizer.all(v, self.index) for v in query]
        elif query_type == 'between':
            query = tuple(query) # collect iterators
            len_query = len(query)
            max_exclude = len_query >= 4 and bool(query[3])
            min_exclude = len_query >= 3 and bool(query[2])
            max = len_query >= 2 and query[1] and self.normalizer.maximum(
                query[1], self.index, max_exclude) or None
            min = len_query >= 1 and query[0] and self.normalizer.minimum(
                query[0], self.index, min_exclude) or None
            res = (min, max, min_exclude, max_exclude)
        else:
            res = query
        return self.index.apply({query_type: res})

    def minValue(self, min=None):
        if min is not None:
            min = self.normalizer.minimum(min, self.index)
        return self.index.minValue(min)

    def maxValue(self, max=None):
        if max is not None:
            max = self.normalizer.maximum(max, self.index)
        return self.index.maxValue(max)

    def values(self, min=None, max=None, excludemin=False, excludemax=False,
               doc_id=None):
        if min is not None:
            min = self.normalizer.minimum(min, self.index)
        if max is not None:
            max = self.normalizer.maximum(max, self.index)
        return self.index.values(min, max, excludemin, excludemax,
                doc_id=doc_id)

    def containsValue(self, value):
        return self.index.containsValue(value)

    def ids(self):
        return self.index.ids()

    @property
    def sort(self):
        # delegate upstream or raise AttributeError
        return self.index.sort


@interface.implementer(zc.catalog.interfaces.ICallableWrapper)
class CallableWrapper(persistent.Persistent):

    converter = None
    index = None

    def __init__(self, index, converter):
        self.index = index
        self.converter = converter

    def index_doc(self, docid, value):
        "See zope.index.interfaces.IInjection"
        self.index.index_doc(docid, self.converter(value))

    def __getattr__(self, name):
        return getattr(self.index, name)


def set_resolution(value, resolution):
    resolution += 2
    if resolution < 6:
        args = []
        args.extend(value.timetuple()[:resolution+1])
        args.extend([0]*(6-resolution))
        args.append(value.tzinfo)
        value = datetime.datetime(*args)
    return value

def get_request():
    i = zope.security.management.queryInteraction()
    if i is not None:
        for p in i.participations:
            if IRequest.providedBy(p):
                return p
    return None

def get_tz(default=pytz.reference.Local):
    request = get_request()
    if request is None:
        return default
    return zope.interface.common.idatetime.ITZInfo(request, default)

def add_tz(value):
    if type(value) is datetime.datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=get_tz())
        return value
    else:
        raise ValueError(value)

def day_end(value):
    return (
        datetime.datetime.combine(
            value, datetime.time(tzinfo=get_tz())) +
        datetime.timedelta(days=1) - # separate for daylight savings
        datetime.timedelta(microseconds=1))

def day_begin(value):
    return datetime.datetime.combine(
        value, datetime.time(tzinfo=get_tz()))


@interface.implementer(zc.catalog.interfaces.IDateTimeNormalizer)
class DateTimeNormalizer(persistent.Persistent):

    def __init__(self, resolution=2):
        self.resolution = resolution
        # 0, 1, 2, 3, 4
        # day, hour, minute, second, microsecond

    def value(self, value):
        if not isinstance(value, datetime.datetime) or value.tzinfo is None:
            raise ValueError(
                _('This index only indexes timezone-aware datetimes.'))
        return set_resolution(value, self.resolution)

    def any(self, value, index):
        if type(value) is datetime.date:
            start = datetime.datetime.combine(
                value, datetime.time(tzinfo=get_tz()))
            stop = start + datetime.timedelta(days=1)
            return index.values(start, stop, False, True)
        return (add_tz(value),)

    def all(self, value, index):
        return add_tz(value)

    def minimum(self, value, index, exclude=False):
        if type(value) is datetime.date:
            if exclude:
                return day_end(value)
            else:
                return day_begin(value)
        return add_tz(value)

    def maximum(self, value, index, exclude=False):
        if type(value) is datetime.date:
            if exclude:
                return day_begin(value)
            else:
                return day_end(value)
        return add_tz(value)

@interface.implementer(
    zope.interface.implementedBy(NormalizationWrapper),
    zope.index.interfaces.IIndexSort,
    zc.catalog.interfaces.IValueIndex)
def DateTimeValueIndex(resolution=2): # 2 == minute; note that hour is good
    # for timezone-aware per-day searches
    ix = NormalizationWrapper(ValueIndex(), DateTimeNormalizer(resolution))
    interface.alsoProvides(ix, zc.catalog.interfaces.IValueIndex)
    return ix

@interface.implementer(
    zope.interface.implementedBy(NormalizationWrapper),
    zc.catalog.interfaces.ISetIndex)
def DateTimeSetIndex(resolution=2): # 2 == minute; note that hour is good
    # for timezone-aware per-day searches
    ix = NormalizationWrapper(SetIndex(), DateTimeNormalizer(resolution), True)
    interface.alsoProvides(ix, zc.catalog.interfaces.ISetIndex)
    return ix
