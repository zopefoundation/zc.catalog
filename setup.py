##############################################################################
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
"""Setup for zc.catalog package

$Id: setup.py 81038 2007-10-24 14:34:17Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname('.'), *rnames)).read()

setup(name='zc.catalog',
      version = '1.3.0',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description="Extensions to the Zope 3 Catalog",
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('src', 'zc', 'catalog', 'valueindex.txt')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'setindex.txt')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'normalizedindex.txt')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'extentcatalog.txt')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'stemmer.txt')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'legacy.txt')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'globber.txt')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'callablewrapper.txt')
          + '\n\n' +
          read('src', 'zc', 'catalog', 'browser', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 i18n date time duration",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://cheeseshop.python.org/pypi/zc.catalog',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zc'],
      extras_require=dict(
           test=['zope.app.authentication',
                 'zope.app.intid',
                 'zope.app.keyreference',
                 'zope.app.securitypolicy',
                 'zope.app.server',
                 'zope.app.testing',
                 'zope.app.zcmlfiles',
                 'zope.securitypolicy',
                 'zope.testbrowser',
                 'zope.testing',
                 ]),
      install_requires=['ZODB3',
                        'pytz',
                        'setuptools',
                        'zope.app.catalog',
                        'zope.app.container',
                        'zope.component',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security',
                        'zope.testing',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
