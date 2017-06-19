#!/usr/bin/env python
from setuptools import setup
import os
import re


def get_version():
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join('mpathy', '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name='django-mpathy',
    description='''Simple hierarchical data using materialised path, in a postgres database.''',
    version=get_version(),
    author='Craig de Stigter',
    author_email='craig.ds@gmail.com',
    url='http://github.com/craigds/django-mpathy',
    packages=['mpathy'],
    install_requires=[
        # Is it even _possible_ to write a python lib without six these days?
        'six',

        # For psycopg2.extensions.quote_ident.
        # Could probably remove this and implement quote_ident ourselves if helpful, it's very simple code
        'psycopg2>=2.7',

        # Django<1.11 would be hard to support:
        #   * (new in 1.11) We use custom indexes. Could implement with custom SQL if *required*
        #   * (new in 1.10) We inject migration operations in a pre_migrate signal.
        #     This would be hard to hack around, so makes supporting 1.8 hard/impossible.
        'Django>=1.11',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Database',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ],
)
