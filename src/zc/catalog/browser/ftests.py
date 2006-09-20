##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional tests for `zc.catalog.browser`.

$Id$
"""
from zope.app.testing.functional import FunctionalDocFileSuite
from zope.testing import doctest

def test_suite():
    return FunctionalDocFileSuite('README.txt',
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite')
