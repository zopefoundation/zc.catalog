##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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

"""
import doctest
import unittest
import transaction
import zope.intid
import zope.intid.interfaces


from zope.processlifetime import IDatabaseOpenedWithRoot
import zope.app.appsetup.bootstrap
from zope.app.wsgi.testlayer import BrowserLayer
from zope.testbrowser.wsgi import TestBrowserLayer


import zc.catalog.browser

class _ZcCatalogLayer(TestBrowserLayer,
                      BrowserLayer):
    pass

ZcCatalogLayer = _ZcCatalogLayer(zc.catalog.browser)


@zope.component.adapter(IDatabaseOpenedWithRoot)
def initializeIntIds(event):
        _db, connection, _root, root_folder = (
            zope.app.appsetup.bootstrap.getInformationFromEvent(event))
        sm = root_folder.getSiteManager()
        if 'test-int-ids' not in sm['default']:
            intids = zope.intid.IntIds()

            sm["default"]["test-int-ids"] = intids
            sm.registerUtility(
                intids,
                zope.intid.interfaces.IIntIds)
            transaction.commit()
        connection.close()

def test_suite():
    suite = doctest.DocFileSuite(
        "README.rst",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    suite.layer = ZcCatalogLayer
    return suite

class LoginLogout(object):
    # dummy to avoid dep on zope.app.security
    def __call__(self):
        return

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
