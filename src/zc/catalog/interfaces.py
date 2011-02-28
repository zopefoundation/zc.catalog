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
"""interfaces for zc.catalog

$Id: interfaces.py 2918 2005-07-19 22:12:38Z jim $
"""

from zope import interface, schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import zope.index.interfaces
import zope.catalog.interfaces
from zc.catalog.i18n import _
import BTrees.Interfaces


class IExtent(interface.Interface):
    """An extent represents the full set of objects indexed by a catalog.
    It is useful for a variety of index operations and catalog queries.
    """

    __parent__ = interface.Attribute(
        """The catalog for which this is an extent; must be None before it is
        set to a catalog""")

    def add(uid, obj):
        """add uid to extent; raise ValueError if it is not addable.

        If uid is already a member of the extent, calling add is a no-op,
        except that if the uid and obj are no longer addable to the extent then
        ValueError is still raised (but without removing the uid)"""

    def remove(uid):
        """Remove uid from set.  Raise KeyError if not a member"""

    def discard(uid):
        """Remove uid from set.  Ignore if not a member"""

    def clear():
        """Remove all uids from set."""

    def __len__():
        """the number of items in the extent."""

    def __iter__():
        """return iterator of uids in set"""

    def __or__(other):
        "Given BTrees.IFBTree data structure, return weighted union"

    def __ror__(other):
        "Given BTrees.IFBTree data structure, return weighted union"

    def union(other, self_weight, other_weight):
        "Given BTrees.IFBTree data structure, return weighted union"

    def __and__(other):
        "Given BTrees.IFBTree data structure, return weighted intersection"

    def __rand__(other):
        "Given BTrees.IFBTree data structure, return weighted intersection"

    def intersection(other, self_weight, other_weight):
        "Given BTrees.IFBTree data structure, return weighted intersection"

    def __sub__(other):
        "extent - set: given BTrees.IFBTree data structure, return difference"

    def difference(other):
        "extent - set: given BTrees.IFBTree data structure, return difference"

    def __rsub__(other):
        "set - extent: given BTrees.IFBTree data structure, return difference"

    def rdifference(other):
        "set - extent: given BTrees.IFBTree data structure, return difference"

    def __nonzero__():
        "return boolean indicating if any uids are in set"

    def __contains__(uid):
        "return boolean indicating if uid is in set"


class IFilterExtent(IExtent):

    filter = interface.Attribute(
        """A (persistent) callable that is passed the extent, a docid, and the
        associated obj and should return a boolean True (is member of extent)
        or False (is not member of extent).""")

    def addable(uid, obj):
        """returns True or False, indicating whether the obj may be added to
        the extent"""


class ISelfPopulatingExtent(IExtent):
    """An extent that knows how to create it's own initial population."""

    populated = schema.Bool(
        title=_("Populated"),
        description=_(
            "Flag indicating whether self-population has been performed."),
        readonly=True,
        )

    def populate():
        """Populate the extent based on the current content of the database.

        After a successful call, `populated` will be True.  Unsuccessful calls
        must raise exceptions.

        If `populated` is true when called, this is a no-op.  After the
        initial population, updates should be maintained via other mechanisms.

        """


class IExtentCatalog(interface.Interface):
    """A catalog of only items within an extent.

    Interface intended to be used with zope.catalog.interfaces.ICatalog"""

    extent = interface.Attribute(
        """An IExtent of the objects cataloged""")


class IIndexValues(interface.Interface):
    """An index that allows introspection of the indexed values"""

    def minValue(min=None):
        """return the minimum value in the index.

        if min is provided, return the minimum value equal to or greater than
        min.

        Raises ValueError if no min.
        """

    def maxValue(max=None):
        """return the maximum value in the index.

        If max is provided, return the maximum value equal to or less than max.

        Raises ValueError if no max.
        """

    def values(min=None, max=None, excludemin=False, excludemax=False,
               doc_id=None):
        """return an iterables of the values in the index.

        if doc_id is provided, returns the values only for that document id.

        If a min is specified, then output is constrained to values greater
        than or equal to the given min, and, if excludemin is specified and
        true, is further constrained to values strictly greater than min.  A
        min value of None is ignored.  If min is None or not specified, and
        excludemin is true, the smallest value is excluded.

        If a max is specified, then output is constrained to values less than
        or equal to the given max, and, if excludemax is specified and
        true, is further constrained to values strictly less than max.  A max
        value of None is ignored.  If max is None or not specified, and
        excludemax is true, the largest value is excluded.
        """

    def containsValue(value):
        """whether the value is used in any of the documents in the index"""

    def ids():
        """return a BTrees.IFBTree data structure of the document ids in the
        index--the ones that have values to be indexed.  All document ids
        should produce at least one value given a call of
        IIndexValues.values(doc_id=id).
        """


class ISetIndex(interface.Interface):

    def apply(query):
        """Return None or an IFBTree Set of the doc ids that match the query.

        query is a dict with one of the following keys: any_of, any,
        all_of, between, and none.

        Any one of the keys may be used; using more than one is not allowed.

        The any_of key should have a value of an iterable of values: the
        result will be the docids whose values contain any of the given values.

        The all_of key should have a value of an iterable of values: the
        result will be the docids whose values contain all of the given values.

        The between key should have a value of an iterable of one to four
        members. The first is the minimum value, or None; the second is the
        maximum value, or None; the third is boolean, defaulting to False,
        declaring if the min should be excluded; and the last is also boolean,
        defaulting to False, declaring if the max should be excluded.

        The any key should take None or an extent.  If the key is None, the
        results will be all docids with any value.  If the key is an extent,
        the results will be the intersection of the extent and all docids with
        any value.

        The none key should take an extent.  It returns the docids in
        the extent that do not have any values in the index.
        """


class IValueIndex(interface.Interface):

    def apply(query):
        """Return None or an IFBTree Set of the doc ids that match the query.

        query is a dict with one of the following keys: any_of, any,
        between, and none.

        Any one of the keys may be used; using more than one is not allowed.

        The any_of key should have a value of an iterable of values: the
        result will be the docids whose values contain any of the given values.

        The between key should have a value of an iterable of one to four
        members. The first is the minimum value, or None; the second is the
        maximum value, or None; the third is boolean, defaulting to False,
        declaring if the min should be excluded; and the last is also boolean,
        defaulting to False, declaring if the max should be excluded.

        The any key should take None or an extent.  If the key is None, the
        results will be all docids with any value.  If the key is an extent,
        the results will be the intersection of the extent and all docids with
        any value.

        The none key should take an extent.  It returns the docids in
        the extent that do not have any values in the index.
        """


class ICatalogValueIndex(zope.catalog.interfaces.IAttributeIndex,
                         zope.catalog.interfaces.ICatalogIndex):
    """Interface-based catalog value index
    """


class ICatalogSetIndex(zope.catalog.interfaces.IAttributeIndex,
                       zope.catalog.interfaces.ICatalogIndex):
    """Interface-based catalog set index
    """


class INormalizationWrapper(zope.index.interfaces.IInjection,
                            zope.index.interfaces.IIndexSearch,
                            zope.index.interfaces.IStatistics,
                            IIndexValues):
    """A wrapper for an index that uses a normalizer to normalize injection
    and querying."""

    index = interface.Attribute(
        """an index implementing IInjection, IIndexSearch, IStatistics, and
        IIndexValues""")

    normalizer = interface.Attribute("a normalizer, implementing INormalizer")

    collection_index = interface.Attribute(
        """boolean: whether indexed values should be treated as collections
        (each composite value normalized) or not (original value is
        normalized)""")


class INormalizer(interface.Interface):

    def value(value):
        """normalize or check constraints for an input value; raise an error
        or return the value to be indexed."""

    def any(value, index):
        """normalize a query value for a "any_of" search; return a sequence of
        values."""

    def all(value, index):
        """Normalize a query value for an "all_of" search; return the value
        for query"""

    def minimum(value, index, exclude=False):
        """normalize a query value for minimum of a range; return the value for
        query"""

    def maximum(value, index, exclude=False):
        """normalize a query value for maximum of a range; return the value for
        query"""

resolution_vocabulary = SimpleVocabulary([SimpleTerm(i, t, t) for i, t in enumerate(
    (_('day'), _('hour'), _('minute'), _('second'), _('microsecond')))])
    #  0         1          2            3            4


class IDateTimeNormalizer(INormalizer):
    resolution = schema.Choice(
        vocabulary=resolution_vocabulary,
        title=_('Resolution'),
        default=2,
        required=True)


class ICallableWrapper(zope.index.interfaces.IInjection,
                       zope.index.interfaces.IIndexSearch,
                       zope.index.interfaces.IStatistics,
                       IIndexValues):
    """A wrapper for an index that uses a callable to convert injection."""

    index = interface.Attribute(
        """An index implementing IInjection, IIndexSearch, IStatistics, and
        IIndexValues""")

    converter = interface.Attribute("A callable converter")
