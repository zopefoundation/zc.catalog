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

$Id: tests.py 2918 2005-07-19 22:12:38Z jim $
"""

import unittest
from zope.testing import doctest, module
import zope.component.testing
import zope.component.factory
import zope.component.interfaces

import zc.catalog
import zc.catalog.interfaces

import BTrees.Interfaces
import BTrees.LOBTree
import BTrees.OLBTree
import BTrees.LFBTree


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
    tests = unittest.TestSuite((
        # 32 bits
        doctest.DocFileSuite(
            'extentcatalog.txt', setUp=modSetUp32bit, tearDown=modTearDown,
            optionflags=doctest.INTERPRET_FOOTNOTES),
        doctest.DocFileSuite(
            'setindex.txt', setUp=setUp32bit, tearDown=tearDown,
            optionflags=doctest.INTERPRET_FOOTNOTES),
        doctest.DocFileSuite(
            'valueindex.txt', setUp=setUp32bit, tearDown=tearDown),
        doctest.DocFileSuite(
            'normalizedindex.txt', setUp=setUp32bit, tearDown=tearDown),
        doctest.DocFileSuite(
            'globber.txt', setUp=setUp32bit, tearDown=tearDown),
        doctest.DocFileSuite(
            'callablewrapper.txt', setUp=setUp32bit, tearDown=tearDown),

        # 64 bits
        doctest.DocFileSuite(
            'extentcatalog.txt', setUp=modSetUp64bit, tearDown=modTearDown,
            optionflags=doctest.INTERPRET_FOOTNOTES),
        doctest.DocFileSuite('setindex.txt', setUp=setUp64bit,
                             tearDown=tearDown),
        doctest.DocFileSuite('valueindex.txt', setUp=setUp64bit,
                             tearDown=tearDown),
        doctest.DocFileSuite('normalizedindex.txt', setUp=setUp64bit,
                             tearDown=tearDown),
        doctest.DocFileSuite('globber.txt', setUp=setUp64bit,
                             tearDown=tearDown),
        doctest.DocFileSuite('callablewrapper.txt', setUp=setUp64bit,
                             tearDown=tearDown),

        # legacy data support
        doctest.DocFileSuite('legacy.txt', optionflags=doctest.ELLIPSIS),
        ))
    import zc.catalog.stemmer
    if not zc.catalog.stemmer.broken:
        tests.addTest(doctest.DocFileSuite('stemmer.txt'))
    return tests

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
