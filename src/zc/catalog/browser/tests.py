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

$Id$
"""
import doctest
import os.path
import unittest
import transaction
import zope.intid
import zope.intid.interfaces

try:
    # Only include the functional tests whenever the required dependencies
    # are installed.
    import zope.app.appsetup.bootstrap
    import zope.app.appsetup.interfaces
    import zope.app.testing.functional
    import zope.app.zcmlfiles
    import zope.app.catalog

    here = os.path.dirname(os.path.realpath(__file__))

    ZcCatalogLayer = zope.app.testing.functional.ZCMLLayer(
        os.path.join(here, "ftesting.zcml"), __name__, "ZcCatalogLayer")

    @zope.component.adapter(
        zope.app.appsetup.interfaces.IDatabaseOpenedWithRootEvent)
    def initializeIntIds(event):
        db, connection, root, root_folder = (
            zope.app.appsetup.bootstrap.getInformationFromEvent(event))
        sm = root_folder.getSiteManager()
        intids = zope.intid.IntIds()
        sm["default"]["test-int-ids"] = intids
        sm.registerUtility(
            intids,
            zope.intid.interfaces.IIntIds)
        transaction.commit()
        connection.close()

    def test_suite():
        suite = zope.app.testing.functional.FunctionalDocFileSuite(
            "README.txt",
            optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
        suite.layer = ZcCatalogLayer
        return suite

except (ImportError,) as e:
    def test_suite():
        return unittest.TestSuite()

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
