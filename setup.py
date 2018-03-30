#!/usr/bin/env python
# Copyright (C) 2018 - 2018 Jens Neuhalfen
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import codecs
import os
import re
import sys

from setuptools import setup, find_packages

###################################################################
MINIMUM_PYTHON_VERSION = '3.4'

NAME = "imapfw"
PACKAGES = find_packages(where=".",exclude=[])
META_PATH = os.path.join("imapfw", "__init__.py")
KEYWORDS = ["imap", "offline", "sync"]
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
INSTALL_REQUIRES = ["typing; python_version < '3.5'"]

ENTRY_POINTS = {'console_scripts': ['imapfw = imapfw.cli:main']}

###################################################################

HERE = os.path.abspath(os.path.dirname(__file__))


def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {0}+ is required.".format(MINIMUM_PYTHON_VERSION))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__[\s]*=[\s]*['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


if __name__ == "__main__":
    check_python_version()

    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("homepage"),
        version=find_meta("version"),
        author=find_meta("author"),
        author_email=find_meta("author_email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("author_email"),
        keywords=KEYWORDS,
        long_description=read("README.md"),
        packages=PACKAGES,
        package_dir={"imapfw": "imapfw"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        entry_points=ENTRY_POINTS,
        include_package_data=True
    )
