================
Callable Wrapper
================

If we want to index some value that is easily derivable from a
document, we have to define an interface with this value as an
attribute, and create an adapter that calculates this value and
implements this interface.  All this is too much hassle if the want to
store a single easily derivable value.   CallableWrapper solves this
problem, by converting the document to the indexed value with a
callable converter.

Here's a contrived example.  Suppose we have cars that know their
mileage expressed in miles per gallon, but we want to index their
economy in litres per 100 km.

    >>> class Car(object):
    ...     def __init__(self, mpg):
    ...         self.mpg = mpg

    >>> def mpg2lp100(car):
    ...     return 100.0/(1.609344/3.7854118 * car.mpg)

Let's create an index that would index cars' l/100 km rating.

    >>> from zc.catalog import index, catalogindex
    >>> idx = catalogindex.CallableWrapper(index.ValueIndex(), mpg2lp100)

Let's add a couple of cars to the index!

    >>> hummer = Car(10.0)
    >>> beamer = Car(22.0)
    >>> civic = Car(45.0)

    >>> idx.index_doc(1, hummer)
    >>> idx.index_doc(2, beamer)
    >>> idx.index_doc(3, civic)

The indexed values should be the converted l/100 km ratings:

    >>> list(idx.values()) # doctest: +ELLIPSIS
    [5.22699076283393..., 10.691572014887601, 23.521458432752723]

We can query for cars that consume fuel in some range:

    >>> list(idx.apply({'between': (5.0, 7.0)}))
    [3]
