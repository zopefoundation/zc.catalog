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
from zope.testing import doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('extentcatalog.txt'),
        doctest.DocFileSuite('setindex.txt'),
        doctest.DocFileSuite('valueindex.txt'),
        doctest.DocFileSuite('normalizedindex.txt'),
        doctest.DocFileSuite('globber.txt'),
        doctest.DocFileSuite('stemmer.txt'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
