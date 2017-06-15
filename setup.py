##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Setup for zc.catalog package

"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    with open(os.path.join(os.path.dirname('.'), *rnames)) as f:
        return f.read()

stemmer_requires = [
    'zopyx.txng3.ext >= 2.0.0',
]

tests_require = [
    'ZODB',
    'zope.annotation',
    'zope.app.appsetup',
    'zope.app.basicskin',
    'zope.app.catalog',
    'zope.app.catalog',
    'zope.app.component',
    'zope.app.container',
    'zope.app.form',
    'zope.app.publisher >= 4.0',
    'zope.app.rotterdam',
    'zope.app.schema >= 4.0',
    'zope.app.wsgi',
    'zope.browsermenu',
    'zope.browserpage',
    'zope.browserresource',
    'zope.dottedname',
    'zope.keyreference',
    'zope.login',
    'zope.password',
    'zope.principalannotation',
    'zope.principalregistry',
    'zope.securitypolicy',
    'zope.testbrowser >= 5.2',
    'zope.testing',
    'zope.testrunner',
] + stemmer_requires

setup(name='zc.catalog',
      version='2.0.1',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description="Extensions to the Zope 3 Catalog",
      long_description=(
          read('README.rst')
          + '\n\n.. contents::\n\n' +
          read('CHANGES.rst')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'valueindex.rst')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'setindex.rst')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'normalizedindex.rst')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'extentcatalog.rst')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'stemmer.rst')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'legacy.rst')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'globber.rst')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'callablewrapper.rst')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'browser', 'README.rst')
          ),
      keywords="zope3 i18n date time duration catalog index",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3',
      ],
      url='http://github.com/zopefoundation/zc.catalog',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['zc'],
      extras_require={
          'test': tests_require,
          'browser': [
              'zope.app.form',
              'zope.browsermenu',
          ],
          'stemmer': stemmer_requires,
      },
      tests_require=tests_require,
      install_requires=[
          'BTrees >= 4.4.1',
          'persistent',
          'pytz',
          'setuptools',
          'zope.catalog >= 4.2.1',
          'zope.component >= 4.3.0',
          'zope.container >= 4.1.0',
          'zope.i18nmessageid >= 4.1.0',
          'zope.index >= 4.3.0',
          'zope.interface >= 4.4.0',
          'zope.intid >= 4.2.0',
          'zope.publisher >= 3.12',
          'zope.schema >= 4.4.2',
          'zope.security >= 4.1.0',
      ],
      include_package_data=True,
      zip_safe=False,
)
