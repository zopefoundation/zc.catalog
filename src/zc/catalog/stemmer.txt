=======
Stemmer
=======

The stemmer uses Andreas Jung's stemmer code, which is a Python wrapper of
M. F. Porter's Snowball project (http://snowball.tartarus.org/index.php).
It is designed to be used as part of a pipeline in a zope/index/text/
lexicon, after a splitter.  This enables getting the relevance ranking
of the zope/index/text code with the splitting functionality of TextIndexNG 3.x.

It requires that the TextIndexNG extensions--specifically txngstemmer--have
been compiled and installed in your Python installation.  Inclusion of the
textindexng package is not necessary.

As of this writing (Jan 3, 2007), installing the necessary extensions can be
done with the following steps:

- `svn co https://svn.sourceforge.net/svnroot/textindexng/extension_modules/trunk ext_mod`
- `cd ext_mod`
- (using the python you use for Zope) `python setup.py install`

Another approach is to simply install TextIndexNG (see
http://opensource.zopyx.com/software/textindexng3)

The stemmer must be instantiated with the language for which stemming is
desired.  It defaults to 'english'.  For what it is worth, other languages
supported as of this writing, using the strings that the stemmer expects,
include the following: 'danish', 'dutch', 'english', 'finnish', 'french',
'german', 'italian', 'norwegian', 'portuguese', 'russian', 'spanish', and
'swedish'.

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
