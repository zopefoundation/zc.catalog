=========
 CHANGES
=========

2.0.1 (2017-06-15)
==================

- Add Python 3 compatibility for the ``zopyx.txng3.ext`` stemmer.
  See https://github.com/zopefoundation/zc.catalog/issues/4.


2.0.0 (2017-05-09)
==================

- Add support for Python 3.4, 3.5, 3.6 and PyPy. Note that the
  ``zopyx.txng3.ext`` stemmer is not available on Python 3.

- Remove test dependency on zope.app.zcmlfiles and zope.app.testing,
  among others.


1.6 (2013-07-04)
================

- Using Python's ``doctest`` module instead of deprecated
  ``zope.testing.doctest``.

- Move ``zope.intid`` to dependencies.


1.5.1 (2012-01-20)
==================

- Fix the extent catalog's `searchResults` method to work when using a
  local uid source.

- Replaced a testing dependency on ``zope.app.authentication`` with
  ``zope.password``.

- Removed ``zope.app.server`` test dependency.


1.5 (2010-10-19)
================

- The package's ``configure.zcml`` does not include the browser subpackage's
  ``configure.zcml`` anymore.

  This, together with ``browser`` and ``test_browser`` ``extras_require``,
  decouples the browser view registrations from the main code. As a result
  projects that do not need the ZMI views to be registered are not pulling in
  the zope.app.* dependencies anymore.

  To enable the ZMI views for your project, you will have to do two things:

  * list ``zc.catalog [browser]`` as a ``install_requires``.

  * have your project's ``configure.zcml`` include the ``zc.catalog.browser``
    subpackage.

- Only include the browser tests whenever the dependencies for the browser
  tests are available.

- Python2.7 test fix.


1.4.5 (2010-10-05)
==================

- Remove implicit test dependency on zope.app.dublincore, that was not needed
  in the first place.


1.4.4 (2010-07-06)
==================

* Fixed test-failure happening with more recent ``mechanize`` (>=2.0).


1.4.3 (2010-03-09)
==================

* Try to import the stemmer from the zopyx.txng3.ext package first, which
  as of 3.3.2 contains stability and memory leak fixes.


1.4.2 (2010-01-20)
==================

* Fix missing testing dependencies when using ZTK by adding zope.login.

1.4.1 (2009-02-27)
==================

* Add FieldIndex-like sorting support for the ValueIndex.

* Add sorting indexes support for the NormalizationWrapper.


1.4.0 (2009-02-07)
==================

* Fixed a typo in ValueIndex addform and addMenuItem

* Use ``zope.container`` instead of ``zope.app.container``.

* Use ``zope.keyreference`` instead of ``zope.app.keyreference``.

* Use ``zope.intid`` instead of ``zope.app.intid``.

* Use ``zope.catalog`` instead of ``zope.app.catalog``.


1.3.0 (2008-09-10)
==================

* Added hook point to allow extent catalog to be used with local UID sources.


1.2.0 (2007-11-03)
==================

* Updated package meta-data.

* zc.catalog now can use 64-bit BTrees ("L") as provided by ZODB 3.8.

* Albertas Agejavas (alga@pov.lt) included the new CallableWrapper, for
  when the typical Zope 3 index-by-adapter story
  (zope.app.catalog.attribute) is unnecessary trouble, and you just want
  to use a callable.  See callablewrapper.txt.  This can also be used for
  other indexes based on the zope.index interfaces.

* Extents now have a __len__.  The current implementation defers to the
  standard BTree len implementation, and shares its performance
  characteristics: it needs to wake up all of the buckets, but if all of the
  buckets are awake it is a fairly quick operation.

* A simple ISelfPoulatingExtent was added to the extentcatalog module for
  which populating is a no-op.  This is directly useful for catalogs that
  are used as implementation details of a component, in which objects are
  indexed explicitly by your own calls rather than by the usual subscribers.
  It is also potentially slightly useful as a base for other self-populating
  extents.


1.1.1 (2007-3-17)
=================

'all_of' would return all results when one of the values had no results.
Reported, with test and fix provided, by Nando Quintana.


1.1 (2007-01-06)
================

Features removed
----------------

The queueing of events in the extent catalog has been entirely removed.
Subtransactions caused significant problems to the code introduced in 1.0.
Other solutions also have significant problems, and the win of this kind
of queueing is qustionable.  Here is a run down of the approaches rejected
for getting the queueing to work:

* _p_invalidate (used in 1.0).  Not really designed for use within a
  transaction, and reverts to last savepoint, rather than the beginning of
  the transaction.  Could monkeypatch savepoints to iterate over
  precommit transaction hooks but that just smells too bad.

* _p_resolveConflict.  Requires application software to exist in ZEO and
  even ZRS installations, which is counter to our software deployment goals.
  Also causes useless repeated writes of empty queue to database, but that's
  not the showstopper.

* vague hand-wavy ideas for separate storages or transaction managers for the
  queue.  Never panned out in discussion.


1.0 (2007-01-05)
================

Bugs fixed
----------

* adjusted extentcatalog tests to trigger (and discuss and test) the queueing
  behavior.

* fixed problem with excessive conflict errors due to queueing code.

* updated stemming to work with newest version of TextIndexNG's extensions.

* omitted stemming test when TextIndexNG's extensions are unavailable, so
  tests pass without it.  Since TextIndexNG's extensions are optional, this
  seems reasonable.

* removed use of zapi in extentcatalog.


0.2 (2006-11-22)
================

Features added
--------------

* First release on Cheeseshop.
