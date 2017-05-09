=============
 Value Index
=============

The valueindex is an index similar to, but more flexible than a standard Zope
field index.  The index allows searches for documents that contain any of a
set of values; between a set of values; any (non-None) values; and any empty
values.

Additionally, the index supports an interface that allows examination of the
indexed values.

It is as policy-free as possible, and is intended to be the engine for indexes
with more policy, as well as being useful itself.

On creation, the index has no wordCount, no documentCount, and is, as
expected, fairly empty.

    >>> from zc.catalog.index import ValueIndex
    >>> index = ValueIndex()
    >>> index.documentCount()
    0
    >>> index.wordCount()
    0
    >>> index.maxValue() # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError:...
    >>> index.minValue() # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError:...
    >>> list(index.values())
    []
    >>> len(index.apply({'any_of': (5,)}))
    0

The index supports indexing any value.  All values within a given index must
sort consistently across Python versions.

    >>> data = {1: 'a',
    ...         2: 'b',
    ...         3: 'a',
    ...         4: 'c',
    ...         5: 'd',
    ...         6: 'c',
    ...         7: 'c',
    ...         8: 'b',
    ...         9: 'c',
    ... }
    >>> for k, v in data.items():
    ...     index.index_doc(k, v)
    ...

After indexing, the statistics and values match the newly entered content.

    >>> list(index.values())
    ['a', 'b', 'c', 'd']
    >>> index.documentCount()
    9
    >>> index.wordCount()
    4
    >>> index.maxValue()
    'd'
    >>> index.minValue()
    'a'
    >>> list(index.ids())
    [1, 2, 3, 4, 5, 6, 7, 8, 9]

The index supports four types of query.  The first is 'any_of'.  It
takes an iterable of values, and returns an iterable of document ids that
contain any of the values.  The results are not weighted.

    >>> list(index.apply({'any_of': ('b', 'c')}))
    [2, 4, 6, 7, 8, 9]
    >>> list(index.apply({'any_of': ('b',)}))
    [2, 8]
    >>> list(index.apply({'any_of': ('d',)}))
    [5]
    >>> bool(index.apply({'any_of': (42,)}))
    False

Another query is 'any', If the key is None, all indexed document ids with any
values are returned.  If the key is an extent, the intersection of the extent
and all document ids with any values is returned.

    >>> list(index.apply({'any': None}))
    [1, 2, 3, 4, 5, 6, 7, 8, 9]

    >>> from zc.catalog.extentcatalog import FilterExtent
    >>> extent = FilterExtent(lambda extent, uid, obj: True)
    >>> for i in range(15):
    ...     extent.add(i, i)
    ...
    >>> list(index.apply({'any': extent}))
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> limited_extent = FilterExtent(lambda extent, uid, obj: True)
    >>> for i in range(5):
    ...     limited_extent.add(i, i)
    ...
    >>> list(index.apply({'any': limited_extent}))
    [1, 2, 3, 4]

The 'between' argument takes from 1 to four values.  The first is the
minimum, and defaults to None, indicating no minimum; the second is the
maximum, and defaults to None, indicating no maximum; the next is a boolean for
whether the minimum value should be excluded, and defaults to False; and the
last is a boolean for whether the maximum value should be excluded, and also
defaults to False.  The results are not weighted.

    >>> list(index.apply({'between': ('b', 'd')}))
    [2, 4, 5, 6, 7, 8, 9]
    >>> list(index.apply({'between': ('c', None)}))
    [4, 5, 6, 7, 9]
    >>> list(index.apply({'between': ('c',)}))
    [4, 5, 6, 7, 9]
    >>> list(index.apply({'between': ('b', 'd', True, True)}))
    [4, 6, 7, 9]

Using an invalid (non-comparable on Python 3) argument to between produces
nothing:

    >>> list(index.apply({'between': (1, 5)}))
    []

The 'none' argument takes an extent and returns the ids in the extent
that are not indexed; it is intended to be used to return docids that have
no (or empty) values.

    >>> list(index.apply({'none': extent}))
    [0, 10, 11, 12, 13, 14]

Trying to use more than one of these at a time generates an error.

    >>> index.apply({'between': (5,), 'any_of': (3,)})
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError:...

Using none of them simply returns None.

    >>> index.apply({}) # returns None

Invalid query names cause ValueErrors.

    >>> index.apply({'foo': ()})
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ValueError:...

When you unindex a document, the searches and statistics should be updated.

    >>> index.unindex_doc(5)
    >>> len(index.apply({'any_of': ('d',)}))
    0
    >>> index.documentCount()
    8
    >>> index.wordCount()
    3
    >>> list(index.values())
    ['a', 'b', 'c']
    >>> list(index.ids())
    [1, 2, 3, 4, 6, 7, 8, 9]

Reindexing a document that has a changed value also is reflected in
subsequent searches and statistic checks.

    >>> list(index.apply({'any_of': ('b',)}))
    [2, 8]
    >>> data[8] = 'e'
    >>> index.index_doc(8, data[8])
    >>> index.documentCount()
    8
    >>> index.wordCount()
    4
    >>> list(index.apply({'any_of': ('e',)}))
    [8]
    >>> list(index.apply({'any_of': ('b',)}))
    [2]
    >>> data[2] = 'e'
    >>> index.index_doc(2, data[2])
    >>> index.documentCount()
    8
    >>> index.wordCount()
    3
    >>> list(index.apply({'any_of': ('e',)}))
    [2, 8]
    >>> list(index.apply({'any_of': ('b',)}))
    []

Reindexing a document for which the value is now None causes it to be removed
from the statistics.

    >>> data[3] = None
    >>> index.index_doc(3, data[3])
    >>> index.documentCount()
    7
    >>> index.wordCount()
    3
    >>> list(index.ids())
    [1, 2, 4, 6, 7, 8, 9]

This affects both ways of determining the ids that are and are not in the index
(that do and do not have values).

    >>> list(index.apply({'any': None}))
    [1, 2, 4, 6, 7, 8, 9]
    >>> list(index.apply({'any': extent}))
    [1, 2, 4, 6, 7, 8, 9]
    >>> list(index.apply({'none': extent}))
    [0, 3, 5, 10, 11, 12, 13, 14]

The values method can be used to examine the indexed values for a given
document id.  For a valueindex, the "values" for a given doc_id will always
have a length of 0 or 1.

    >>> index.values(doc_id=8)
    ('e',)

And the containsValue method provides a way of determining membership in the
values.

    >>> index.containsValue('a')
    True
    >>> index.containsValue('q')
    False

Sorting Value Indexes
=====================

Value indexes supports sorting, just like zope.index.field.FieldIndex.

    >>> index.clear()

    >>> index.index_doc(1, 9)
    >>> index.index_doc(2, 8)
    >>> index.index_doc(3, 7)
    >>> index.index_doc(4, 6)
    >>> index.index_doc(5, 5)
    >>> index.index_doc(6, 4)
    >>> index.index_doc(7, 3)
    >>> index.index_doc(8, 2)
    >>> index.index_doc(9, 1)

    >>> list(index.sort([4, 2, 9, 7, 3, 1, 5]))
    [9, 7, 5, 4, 3, 2, 1]

We can also specify the ``reverse`` argument to reverse results:

    >>> list(index.sort([4, 2, 9, 7, 3, 1, 5], reverse=True))
    [1, 2, 3, 4, 5, 7, 9]

And as per IIndexSort, we can limit results by specifying the ``limit``
argument:

    >>> list(index.sort([4, 2, 9, 7, 3, 1, 5], limit=3))
    [9, 7, 5]

If we pass an id that is not indexed by this index, it won't be included
in the result.

    >>> list(index.sort([2, 10]))
    [2]
