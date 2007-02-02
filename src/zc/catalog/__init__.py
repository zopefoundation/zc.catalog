#############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""zc.component package

"""
import BTrees.Interfaces
import BTrees.IFBTree


class BTreeAPI32(object):
    """IFTree components and merge functions.

    This class can be used as a pickleable reference to a particular
    flavour of BTrees used in an index or catalog (IFBTrees in this case).
    """

    TreeSet = BTrees.IFBTree.IFTreeSet
    Set = BTrees.IFBTree.IFSet
    Bucket = BTrees.IFBTree.IFBucket

    # IMerge
    difference = BTrees.IFBTree.difference
    union = BTrees.IFBTree.union
    intersection = BTrees.IFBTree.intersection

    # IIMerge
    weightedUnion = BTrees.IFBTree.weightedUnion
    weightedIntersection = BTrees.IFBTree.weightedIntersection

    # IMergeIntegerKey
    multiunion = BTrees.IFBTree.multiunion


try:
    import BTrees.LFBTree
except:
    pass
else:
    class BTreeAPI64(object):
        """IFTree components and merge functions.

        This class can be used as a pickleable reference to a particular
        flavour of BTrees used in an index or catalog (LFBTrees in this case).
        """

        TreeSet = BTrees.LFBTree.LFTreeSet
        Set = BTrees.LFBTree.LFSet
        Bucket = BTrees.LFBTree.LFBucket

        # IMerge
        difference = BTrees.LFBTree.difference
        union = BTrees.LFBTree.union
        intersection = BTrees.LFBTree.intersection

        # IIMerge
        weightedUnion = BTrees.LFBTree.weightedUnion
        weightedIntersection = BTrees.LFBTree.weightedIntersection

        # IMergeIntegerKey
        multiunion = BTrees.LFBTree.multiunion
