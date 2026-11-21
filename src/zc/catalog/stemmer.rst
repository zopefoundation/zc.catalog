=======
Stemmer
=======

The stemmer uses the `snowballstemmer`_ package, which provides the stemming
algorithms of M. F. Porter's Snowball project (https://snowballstem.org/).
It is designed to be used as part of a pipeline in a zope/index/text/
lexicon, after a splitter.

It requires that ``snowballstemmer`` is installed, e. g. by installing
``zc.catalog[stemmer]``.  If it is missing, words are not stemmed at all.

The stemmer must be instantiated with the language for which stemming is
desired.  It defaults to 'english'.  ``snowballstemmer.algorithms()`` returns
the names of the supported languages.

.. _snowballstemmer: https://pypi.org/project/snowballstemmer/

For instance, let's build an index with an english stemmer.

    >>> from zope.index.text import textindex, lexicon
    >>> import zc.catalog.stemmer
    >>> lex = lexicon.Lexicon(
    ...     lexicon.Splitter(), lexicon.CaseNormalizer(),
    ...     lexicon.StopWordRemover(), zc.catalog.stemmer.Stemmer('english'))
    >>> ix = textindex.TextIndex(lex)
    >>> data = [
    ...     (0, 'consigned consistency consoles the constables'),
    ...     (1, 'knaves kneeled and knocked knees, knowing no knights')]
    >>> for doc_id, text in data:
    ...     ix.index_doc(doc_id, text)
    ...
    >>> list(ix.apply('consoling a constable'))
    [0]
    >>> list(ix.apply('knightly kneel'))
    [1]

Note that query terms with globbing characters are not stemmed.

    >>> list(ix.apply('constables*'))
    []
