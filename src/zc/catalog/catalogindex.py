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
"""Indexes appropriate for zope.catalog

$Id: catalogindex.py 2918 2005-07-19 22:12:38Z jim $
"""
import zope.interface

import zope.catalog.attribute
import zope.container.contained
import zope.index.interfaces

import zc.catalog.index
import zc.catalog.interfaces

class ValueIndex(zope.catalog.attribute.AttributeIndex,
                 zc.catalog.index.ValueIndex,
                 zope.container.contained.Contained):

    zope.interface.implements(zc.catalog.interfaces.ICatalogValueIndex)

class SetIndex(zope.catalog.attribute.AttributeIndex,
               zc.catalog.index.SetIndex,
               zope.container.contained.Contained):

    zope.interface.implements(zc.catalog.interfaces.ICatalogSetIndex)

class NormalizationWrapper(
    zope.catalog.attribute.AttributeIndex,
    zc.catalog.index.NormalizationWrapper,
    zope.container.contained.Contained):

    pass


class CallableWrapper(zc.catalog.index.CallableWrapper,
                      zope.container.contained.Contained):
    zope.interface.implements(zc.catalog.interfaces.ICallableWrapper)


@zope.interface.implementer(
    zope.interface.implementedBy(NormalizationWrapper),
    zc.catalog.interfaces.IValueIndex,
    zope.index.interfaces.IIndexSort)
def DateTimeValueIndex(
    field_name=None, interface=None, field_callable=False,
    resolution=2): # hour; good for per-day searches
    ix = NormalizationWrapper(
        field_name, interface, field_callable, zc.catalog.index.ValueIndex(),
        zc.catalog.index.DateTimeNormalizer(resolution), False)
    zope.interface.alsoProvides(ix, zc.catalog.interfaces.IValueIndex)
    return ix

@zope.interface.implementer(
    zope.interface.implementedBy(NormalizationWrapper),
    zc.catalog.interfaces.ISetIndex)
def DateTimeSetIndex(
    field_name=None, interface=None, field_callable=False, 
    resolution=2): # hour; good for per-day searches
    ix = NormalizationWrapper(
        field_name, interface, field_callable, zc.catalog.index.SetIndex(),
        zc.catalog.index.DateTimeNormalizer(resolution), True)
    zope.interface.alsoProvides(ix, zc.catalog.interfaces.ISetIndex)
    return ix
