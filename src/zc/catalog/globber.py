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
"""glob all terms at the end.

$Id: globber.py 2918 2005-07-19 22:12:38Z jim $
"""
from zope.index.text import queryparser, parsetree

reconstitute = {}
reconstitute["NOT"] = lambda nd: "not %s" % (
    reconstitute[nd.getValue().nodeType()](nd.getValue()),)
reconstitute["AND"] = lambda nd: "(%s)" % (" and ".join(expand(nd)),)
reconstitute["OR"] = lambda nd: "(%s)" % (" or ".join(expand(nd)),)
reconstitute["ATOM"] = lambda nd: '%s*' % (nd.getValue())
reconstitute["PHRASE"] = lambda nd: '"%s"' % (
    ' '.join((v + '*') for v in nd.getValue()),)
reconstitute["GLOB"] = lambda nd: nd.getValue()

expand = lambda nd: [reconstitute[n.nodeType()](n) for n in nd.getValue()]

def glob(query, lexicon): # lexicon is index.lexicon
    try:
        tree = queryparser.QueryParser(lexicon).parseQuery(query)
    except parsetree.ParseError:
        return None
    if tree is not None:
        return reconstitute[tree.nodeType()](tree)
    else:
        return None
