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
"""catalog package test runner

"""
import re
import unittest
import doctest
from zope.testing import module
import zope.component.testing
import zope.component.factory
import zope.component.interfaces

from zope.testing import renormalizing

import zc.catalog
from zc.catalog import index
from zc.catalog import extentcatalog
from zc.catalog import globber
from zc.catalog import catalogindex
from zc.catalog import stemmer
import zc.catalog.interfaces

import BTrees.Interfaces
import BTrees.LOBTree
import BTrees.OLBTree
import BTrees.LFBTree

class TestAbstractIndex(unittest.TestCase):

    def test_family_on_cls(self):
        self.assertIsInstance(index.AbstractIndex.family,
                              index.FamilyProperty)

    def test_clear_cruft(self):
        i = index.AbstractIndex()
        i.__dict__['BTreeAPI'] = None
        del i.__dict__['family']
        self.assertIn('BTreeAPI', i.__dict__)
        getattr(i, 'family')
        self.assertNotIn('BTreeAPI', i.__dict__)

    def test_family(self):
        class Family(object):
            class OO(object):
                class BTree(object):
                    pass
            IO = OO
        i = index.AbstractIndex(family=Family)
        self.assertIs(i.family, Family)

    def test_empty_values(self):
        i = index.AbstractIndex()
        res = i.values(doc_id=1)
        self.assertEqual((), res)

class TestValueIndex(unittest.TestCase):

    def test_empty_values(self):
        i = index.ValueIndex()
        res = i.values(doc_id=1)
        self.assertEqual((), res)

class TestSetIndex(unittest.TestCase):

    def test_removed(self):
        i = index.SetIndex()
        i.index_doc(1, ('foo', 'bar'))
        i.index_doc(1, ('foo',))

        self.assertEqual(1, i.wordCount.value)

    def test_appy_all_of_empty(self):
        i = index.SetIndex()
        res = i.apply({'all_of': ()})
        self.assertEqual(len(res), 0)

class TestNormalizationWrapper(unittest.TestCase):

    def test_pass_to_index(self):
        i = index.SetIndex()
        class Normaziler(object):
            @classmethod
            def value(cls, v):
                return v
        n = index.NormalizationWrapper(i, Normaziler)

        self.assertEqual(i.documentCount(), n.documentCount())
        self.assertEqual(i.wordCount(), n.wordCount())
        n.clear()

        n.index_doc(1, ('foo',))
        self.assertEqual(i.wordCount(), n.wordCount())

        self.assertEqual(n.containsValue('foo'), i.containsValue('foo'))

class TestExtent(unittest.TestCase):

    def test_BTreeAPI(self):
        i = extentcatalog.Extent()
        self.assertIsNotNone(i.BTreeAPI)

    def test_bool(self):
        i = extentcatalog.Extent()
        self.assertFalse(i)
        i.add(1, None)
        self.assertTrue(i)
        self.assertEqual(1, len(i))

    def test_discard_missing(self):
        i = extentcatalog.Extent()
        i.discard(0)
        self.assertEqual(0, len(i))

    def test_catalog_update(self):
        from zope.interface.interfaces import ComponentLookupError
        c = extentcatalog.Catalog(extentcatalog.Extent())
        i = index.SetIndex()
        i.__parent__ = None
        self.assertRaises(ComponentLookupError, c.updateIndex, i)

class TestGlob(unittest.TestCase):

    def test_bad_parse(self):
        class Lexicon(object):
            pass
        res = globber.glob('', Lexicon())
        self.assertIsNone(res)

class TestCatalogIndex(unittest.TestCase):

    def test_datetimevalueindex(self):
        i = catalogindex.DateTimeValueIndex(field_name='foo')
        self.assertTrue(zc.catalog.interfaces.IValueIndex.providedBy(i))

    def test_datetimesetindex(self):
        i = catalogindex.DateTimeSetIndex(field_name='foo')
        self.assertTrue(zc.catalog.interfaces.ISetIndex.providedBy(i))


@unittest.skipUnless(stemmer.broken, "Only for broken stemmers")
class TestBrokenStemmer(unittest.TestCase):

    def test_broken(self):
        s = stemmer.Stemmer()
        self.assertIs(stemmer.broken, s.stemmer)
        self.assertEqual('word', s.stemmer.stem("word"))

def setUp32bit(test):
    zope.component.testing.setUp(test)
    test.globs["btrees_family"] = BTrees.family32

def modSetUp32bit(test):
    setUp32bit(test)
    module.setUp(test, 'zc.catalog.doctest_test')

def setUp64bit(test):
    zope.component.testing.setUp(test)
    test.globs["btrees_family"] = BTrees.family64

def modSetUp64bit(test):
    setUp64bit(test)
    module.setUp(test, 'zc.catalog.doctest_test')

def tearDown(test):
    zope.component.testing.tearDown(test)

def modTearDown(test):
    module.tearDown(test)
    zope.component.testing.tearDown(test)


def test_suite():
    checker = renormalizing.RENormalizing((
        (re.compile(r"<class 'BTrees."), "<type 'BTrees."),
    ))
    tests = unittest.TestSuite((
        # 32 bits
        doctest.DocFileSuite(
            'extentcatalog.rst', setUp=modSetUp32bit, tearDown=modTearDown),
        doctest.DocFileSuite(
            'setindex.rst', setUp=setUp32bit, tearDown=tearDown),
        doctest.DocFileSuite(
            'valueindex.rst', setUp=setUp32bit, tearDown=tearDown),
        doctest.DocFileSuite(
            'normalizedindex.rst', setUp=setUp32bit, tearDown=tearDown),
        doctest.DocFileSuite(
            'globber.rst', setUp=setUp32bit, tearDown=tearDown),
        doctest.DocFileSuite(
            'callablewrapper.rst', setUp=setUp32bit, tearDown=tearDown),

        # 64 bits
        doctest.DocFileSuite(
            'extentcatalog.rst', setUp=modSetUp64bit, tearDown=modTearDown),
        doctest.DocFileSuite('setindex.rst', setUp=setUp64bit,
                             tearDown=tearDown),
        doctest.DocFileSuite('valueindex.rst', setUp=setUp64bit,
                             tearDown=tearDown),
        doctest.DocFileSuite('normalizedindex.rst', setUp=setUp64bit,
                             tearDown=tearDown),
        doctest.DocFileSuite('globber.rst', setUp=setUp64bit,
                             tearDown=tearDown),
        doctest.DocFileSuite('callablewrapper.rst', setUp=setUp64bit,
                             tearDown=tearDown),

        # legacy data support
        doctest.DocFileSuite(
            'legacy.rst',
            optionflags=doctest.ELLIPSIS,
            checker=checker),
        ))

    if not stemmer.broken: # pragma: no cover
        tests.addTest(doctest.DocFileSuite('stemmer.rst'))

    tests.addTest(unittest.defaultTestLoader.loadTestsFromName(__name__))
    return tests

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
