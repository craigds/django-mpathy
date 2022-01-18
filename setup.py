#!/usr/bin/env python
from setuptools import setup
import os
import re


def get_version():
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join("mpathy", "__init__.py")).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name="django-mpathy",
    description="""Simple hierarchical data using materialised path, in a postgres database.""",
    version=get_version(),
    author="Craig de Stigter",
    author_email="craig.ds@gmail.com",
    url="http://github.com/craigds/django-mpathy",
    packages=["mpathy"],
    install_requires=[
        "psycopg2>=2.7",
        "Django>=2.2",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Database",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
)
