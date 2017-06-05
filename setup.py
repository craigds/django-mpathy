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
    install_requires=['six'],
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
