==========================
zc.catalog Browser Support
==========================

The zc.catalog.browser package adds simple TTW addition/inspection for SetIndex
and ValueIndex.

First, we need a browser so we can test the web UI.

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.addHeader('Accept-Language', 'en-US')
    >>> browser.open('http://localhost')

Now we need to add the catalog that these indexes are going to reside within.

    >>> browser.open('/++etc++site/default/@@contents.html')
    >>> browser.getLink('Add').click()
    >>> browser.getControl('Catalog').click()
    >>> browser.getControl(name='id').value = 'catalog'
    >>> browser.getControl('Add').click()


SetIndex
--------

Add the SetIndex to the catalog.

    >>> browser.getLink('Add').click()
    >>> browser.getControl('Set Index').click()
    >>> browser.getControl(name='id').value = 'set_index'
    >>> browser.getControl('Add').click()

The add form needs values for what interface to adapt candidate objects to, and
what field name to use, and whether-or-not that field is a callable. (We'll use
a simple interfaces for demonstration purposes, it's not really significant.)

    >>> browser.getControl('Interface', index=0).displayValue = [
    ...     'zope.size.interfaces.ISized']
    >>> browser.getControl('Field Name').value = 'sizeForSorting'
    >>> browser.getControl('Field Callable').click()
    >>> browser.getControl(name='add_input_name').value = 'set_index'
    >>> browser.getControl('Add').click()

Now we can look at the index and see how is is configured.

    >>> browser.getLink('set_index').click()
    >>> print browser.contents
    <...
    ...Interface...zope.size.interfaces.ISized...
    ...Field Name...sizeForSorting...
    ...Field Callable...True...

We need to go back to the catalog so we can add a different index.

    >>> browser.open('/++etc++site/default/catalog/@@contents.html')


ValueIndex
----------

Add the ValueIndex to the catalog.

    >>> browser.getLink('Add').click()
    >>> browser.getControl('Value Index').click()
    >>> browser.getControl(name='id').value = 'value_index'
    >>> browser.getControl('Add').click()

The add form needs values for what interface to adapt candidate objects to, and
what field name to use, and whether-or-not that field is a callable. (We'll use
a simple interfaces for demonstration purposes, it's not really significant.)

    >>> browser.getControl('Interface', index=0).displayValue = [
    ...     'zope.size.interfaces.ISized']
    >>> browser.getControl('Field Name').value = 'sizeForSorting'
    >>> browser.getControl('Field Callable').click()
    >>> browser.getControl(name='add_input_name').value = 'value_index'
    >>> browser.getControl('Add').click()

Now we can look at the index and see how is is configured.

    >>> browser.getLink('value_index').click()
    >>> print browser.contents
    <...
    ...Interface...zope.size.interfaces.ISized...
    ...Field Name...sizeForSorting...
    ...Field Callable...True...

