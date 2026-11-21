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
"""A stemmer based on snowballstemmer.

"""
import re


broken = None
try:
    import snowballstemmer
except ModuleNotFoundError:  # pragma: no cover
    snowballstemmer = None

    class Broken:
        def stemWord(self, word):
            return word
    broken = Broken()


class Stemmer:

    def __init__(self, language='english'):
        self.language = language

    @property
    def stemmer(self):
        if snowballstemmer is None:
            return broken
        return snowballstemmer.stemmer(self.language)

    rxGlob = re.compile(r"[*?]")  # See globToWordIds() in
    # zope/index/text/lexicon.py

    def process(self, lst):
        stemmer = self.stemmer
        result = []
        for s in lst:
            try:
                s = s.decode('utf-8') if isinstance(s, bytes) else s
            except UnicodeDecodeError:  # pragma: no cover
                pass
            else:
                s = stemmer.stemWord(s)
            result.append(s)
        return result

    def processGlob(self, lst):
        stemmer = self.stemmer
        result = []
        rxGlob = self.rxGlob
        for s in lst:
            if not rxGlob.search(s):
                try:
                    s = s.decode('utf-8') if isinstance(s, bytes) else s
                except UnicodeDecodeError:  # pragma: no cover
                    pass
                else:
                    s = stemmer.stemWord(s)
            result.append(s)
        return result
