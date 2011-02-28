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
"""A stemmer based on the textindexng stemmer, itself based on snowball.

$Id: stemmer.py 2918 2005-07-19 22:12:38Z jim $
"""
import re
broken = None
try:
    from zopyx.txng3.ext import stemmer
except ImportError:
    try:
        from zopyx.txng3 import stemmer
    except ImportError:
        try:
            import txngstemmer as stemmer
        except ImportError:
            stemmer = None
            class Broken:
                def stem(self, l):
                    return l
            broken = Broken()

# as of this writing, trying to persist a txngstemmer.Stemmer makes the python
# process end, only printing a "Bus error" message before quitting.  Don't do
# that. July 16 2005
# 2010-03-09 While Stemmer still isn't pickleable, zopyx.txng3.ext 3.3.2 fixes
# the crashes.

class Stemmer(object):

    def __init__(self, language='english'):
        self.language = language

    @property
    def stemmer(self):
        if stemmer is None:
            return broken
        return stemmer.Stemmer(self.language)

    rxGlob = re.compile(r"[*?]") # See globToWordIds() in
    # zope/index/text/lexicon.py

    def process(self, lst):
        stemmer = self.stemmer
        result = []
        for s in lst:
            try:
                s = unicode(s)
            except UnicodeDecodeError:
                pass
            else:
                s = stemmer.stem((s,))[0]
            result.append(s)
        return result

    def processGlob(self, lst):
        stemmer = self.stemmer
        result = []
        rxGlob = self.rxGlob
        for s in lst:
            if not rxGlob.search(s):
                try:
                    s = unicode(s)
                except UnicodeDecodeError:
                    pass
                else:
                    s = stemmer.stem((s,))[0]
            result.append(s)
        return result
