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

$Id: index.py 2918 2005-07-19 22:12:38Z jim $
"""
import datetime
import pytz.reference
import persistent
from BTrees import IFBTree, OOBTree, IOBTree, Length

from zope import component, interface
import zope.interface.common.idatetime
import zope.index.interfaces
import zope.security.management
from zope.publisher.interfaces import IRequest

import zc.catalog.interfaces
from zc.catalog.i18n import _

class AbstractIndex(persistent.Persistent):

    interface.implements(zope.index.interfaces.IInjection,
                         zope.index.interfaces.IIndexSearch,
                         zope.index.interfaces.IStatistics,
                         zc.catalog.interfaces.IIndexValues,
                         )

    def __init__(self):
        self.clear()

    def clear(self):
        self.values_to_documents = OOBTree.OOBTree()
        self.documents_to_values = IOBTree.IOBTree()
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
        return bool(self.values_to_documents.has_key(value))

    def ids(self):
        return self.documents_to_values.keys()

def parseQuery(query):
    if isinstance(query, dict):
        if len(query) > 1:
            raise ValueError(
                'may only pass one of key, value pair')
        elif not query:
            return None, None
        query_type, query = query.items()[0]
        query_type = query_type.lower()
    else:
        raise ValueError('may only pass a dict to apply')
    return query_type, query

class ValueIndex(AbstractIndex):

    interface.implements(zc.catalog.interfaces.IValueIndex)

    def _add_value(self, doc_id, added):
        values_to_documents = self.values_to_documents
        docs = values_to_documents.get(added)
        if docs is None:
            values_to_documents[added] = IFBTree.IFTreeSet((doc_id,))
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
            res = IFBTree.multiunion(
                [s for s in (values_to_documents.get(v) for v in query)
                 if s is not None])
        elif query_type == 'any':
            if query is None:
                res = IFBTree.IFSet(self.ids())
            else:
                assert zc.catalog.interfaces.IExtent.providedBy(query)
                res = query & IFBTree.IFSet(self.ids())
        elif query_type == 'between':
            res = IFBTree.multiunion(
                [s for s in (values_to_documents.get(v) for v in
                             values_to_documents.keys(*query))
                 if s is not None])
        elif query_type == 'none':
            assert zc.catalog.interfaces.IExtent.providedBy(query)
            res = query - IFBTree.IFSet(self.ids())
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

class SetIndex(AbstractIndex):

    interface.implements(zc.catalog.interfaces.ISetIndex)

    def _add_values(self, doc_id, added):
        values_to_documents = self.values_to_documents
        for v in added:
            docs = values_to_documents.get(v)
            if docs is None:
                values_to_documents[v] = IFBTree.IFTreeSet((doc_id,))
                self.wordCount.change(1)
            else:
                docs.insert(doc_id)

    def index_doc(self, doc_id, value):
        new = OOBTree.OOTreeSet(v for v in value if v is not None)
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
                removed = OOBTree.difference(old, new)
                added = OOBTree.difference(new, old)
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
            res = IFBTree.IFBucket()
            for v in query:
                _, res = IFBTree.weightedUnion(
                    res, values_to_documents.get(v))
        elif query_type == 'any':
            if query is None:
                res = IFBTree.IFSet(self.ids())
            else:
                assert zc.catalog.interfaces.IExtent.providedBy(query)
                res = query & IFBTree.IFSet(self.ids())
        elif query_type == 'all_of':
            res = None
            values = iter(query)
            empty = IFBTree.IFTreeSet()
            try:
                res = values_to_documents.get(values.next(), empty)
            except StopIteration:
                res = empty
            while res:
                try:
                    v = values.next()
                except StopIteration:
                    break
                res = IFBTree.intersection(
                    res, values_to_documents.get(v, empty))
        elif query_type == 'between':
            res = IFBTree.IFBucket()
            for v in values_to_documents.keys(*query):
                _, res = IFBTree.weightedUnion(res, values_to_documents.get(v))
        elif query_type == 'none':
            assert zc.catalog.interfaces.IExtent.providedBy(query)
            res = query - IFBTree.IFSet(self.ids())
        else:
            raise ValueError(
                "unknown query type", query_type)
        return res

class NormalizationWrapper(persistent.Persistent):

    interface.implements(zc.catalog.interfaces.INormalizationWrapper)

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

class DateTimeNormalizer(persistent.Persistent):

    interface.implements(zc.catalog.interfaces.IDateTimeNormalizer)
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
    zc.catalog.interfaces.IValueIndex)
def DateTimeValueIndex(resolution=2): # 2 == minute; note that hour is good
    # for timezone-aware per-day searches
    ix = NormalizationWrapper(ValueIndex(), DateTimeNormalizer(resolution))
    interface.directlyProvides(ix, zc.catalog.interfaces.IValueIndex)
    return ix

@interface.implementer(
    zope.interface.implementedBy(NormalizationWrapper),
    zc.catalog.interfaces.ISetIndex)
def DateTimeSetIndex(resolution=2): # 2 == minute; note that hour is good
    # for timezone-aware per-day searches
    ix = NormalizationWrapper(SetIndex(), DateTimeNormalizer(resolution), True)
    interface.directlyProvides(ix, zc.catalog.interfaces.ISetIndex)    
    return ix
