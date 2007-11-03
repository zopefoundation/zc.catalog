=======
Globber
=======

The globber takes a query and makes any term that isn't already a glob into
something that ends in a star.  It was originally envisioned as a *very* low-
rent stemming hack.  The author now questions its value, and hopes that the new
stemming pipeline option can be used instead.  Nonetheless, here is an example
of it at work.

    >>> from zope.index.text import textindex
    >>> index = textindex.TextIndex()
    >>> lex = index.lexicon
    >>> from zc.catalog import globber
    >>> globber.glob('foo bar and baz or (b?ng not boo)', lex)
    '(((foo* and bar*) and baz*) or (b?ng and not boo*))'
