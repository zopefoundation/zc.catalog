import os
from setuptools import setup, find_packages

setup(
    name="zc.catalog",
    version="1.2dev",
    packages=find_packages('src', exclude=["*.tests", "*.ftests"]),
    
    package_dir= {'':'src'},
    
    namespace_packages=['zc'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },
    url='http://svn.zope.org/zc.catalog',
    zip_safe=False,
    author='Zope Project',
    author_email='zope3-dev@zope.org',
    description="zc.catalog contains a number of extensions to the Zope 3 catalog",
    long_description=(
        open('README.txt').read() + '\n' +
        open('src/zc/catalog/CHANGES.txt').read()),
    license='ZPL',
    keywords="zope zope3 indexing",
    classifiers = ['Framework :: Zope3'],
    install_requires=['setuptools',
                      'zope.component',
                      'zope.testing',
                      'ZODB3',
                      'zope.schema',
                      'zope.interface',
                      'zope.app.catalog',
                      'pytz',
                      'zope.security',
                      'zope.publisher',
                      'zope.i18nmessageid',
                      'zope.app.container',
                      ],
    )
