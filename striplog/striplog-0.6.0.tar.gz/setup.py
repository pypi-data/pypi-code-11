#!/usr/bin/env python
# -*- coding: utf 8 -*-
"""
Python installation file.
"""
from setuptools import setup
import re

verstr = 'unknown'
VERSIONFILE = "striplog/_version.py"
with open(VERSIONFILE, "r")as f:
    verstrline = f.read().strip()
    pattern = re.compile(r"__version__ = ['\"](.*)['\"]")
    mo = pattern.search(verstrline)
if mo:
    verstr = mo.group(1)
    print("Version "+verstr)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

REQUIREMENTS = ['numpy',
                'matplotlib'
                ]

TEST_REQUIREMENTS = ['pytest',
                     'coveralls',
                     'pytest-cov',
                     'pytest-mpl'
                     ]

# Test command is:
# py.test --mpl --cov striplog

CLASSIFIERS = ['Development Status :: 4 - Beta',
               'Intended Audience :: Science/Research',
               'Natural Language :: English',
               'License :: OSI Approved :: Apache Software License',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3.3',
               'Programming Language :: Python :: 3.4',
               'Programming Language :: Python :: 3.5',
               ]

setup(name='striplog',
      version=verstr,
      description='Tools for making and managing striplogs.',
      url='http://github.com/agile-geoscience/striplog',
      author='Agile Geoscience',
      author_email='hello@agilegeoscience.com',
      license='Apache 2',
      packages=['striplog'],
      tests_require=TEST_REQUIREMENTS,
      test_suite='run_tests',
      install_requires=REQUIREMENTS,
      classifiers=CLASSIFIERS,
      zip_safe=False,
      )
