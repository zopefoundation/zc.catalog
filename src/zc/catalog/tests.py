#############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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


def modSetUp(test):
    zope.component.testing.setUp(test)
    module.setUp(test, 'zc.catalog.doctest_test')

def modTearDown(test):
    module.tearDown(test)
    zope.component.testing.tearDown(test)


def setUp64bit(test):
    zope.component.testing.setUp(test)
    zope.component.provideUtility(
        zope.component.factory.Factory(BTrees.LOBTree.LOBTree),
        name='IOBTree')
    zope.component.provideUtility(
        zope.component.factory.Factory(BTrees.OLBTree.OLBTree),
        name='OIBTree')
    zope.component.provideUtility(
        zope.component.factory.Factory(BTrees.LFBTree.LFTreeSet),
        name='IFTreeSet')


def tearDown64bit(test):
    zope.component.testing.tearDown(test)


def modSetUp64bit(test):
    setUp64bit(test)
    module.setUp(test, 'zc.catalog.doctest_test')


def test_suite():
    tests = unittest.TestSuite((
        # 32 bits
        doctest.DocFileSuite(
            'extentcatalog.txt', setUp=modSetUp, tearDown=modTearDown,
            optionflags=doctest.INTERPRET_FOOTNOTES),
        doctest.DocFileSuite(
            'setindex.txt', optionflags=doctest.INTERPRET_FOOTNOTES),
        doctest.DocFileSuite('valueindex.txt'),
        doctest.DocFileSuite('normalizedindex.txt'),
        doctest.DocFileSuite('globber.txt'),
        doctest.DocFileSuite('callablewrapper.txt'),

        # 64 bits
        doctest.DocFileSuite(
            'extentcatalog.txt', setUp=modSetUp64bit, tearDown=tearDown64bit,
            optionflags=doctest.INTERPRET_FOOTNOTES),
        doctest.DocFileSuite('setindex.txt', setUp=setUp64bit,
                             tearDown=tearDown64bit),
        doctest.DocFileSuite('valueindex.txt', setUp=setUp64bit,
                             tearDown=tearDown64bit),
        doctest.DocFileSuite('normalizedindex.txt', setUp=setUp64bit,
                             tearDown=tearDown64bit),
        doctest.DocFileSuite('globber.txt', setUp=setUp64bit,
                             tearDown=tearDown64bit),
        doctest.DocFileSuite('callablewrapper.txt', setUp=setUp64bit,
                             tearDown=tearDown64bit),
        ))
    import zc.catalog.stemmer
    if not zc.catalog.stemmer.broken:
        tests.addTest(doctest.DocFileSuite('stemmer.txt'))
    return tests

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
