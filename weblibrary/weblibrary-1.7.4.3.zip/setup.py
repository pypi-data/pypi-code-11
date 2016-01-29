#!/usr/bin/env python

import sys
from os.path import join, dirname

sys.path.append(join(dirname(__file__), 'src'))
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

execfile(join(dirname(__file__), 'src', 'Selenium2Library', 'version.py'))

DESCRIPTION = """
WebLibrary is a web testing library for Robot Framework
that leverages the Selenium 2 (WebDriver) libraries.
"""[1:-1]

setup(name         = 'weblibrary',
      version      = VERSION,
      description  = 'Web testing library for Robot Framework',
      long_description = open(join(dirname(__file__), 'README.rst')).read(),
      author       = 'Dong Hao',
      author_email = '<longmazhanfeng@gmail.com>',
      url          = ' ',
      license      = 'Apache License 2.0',
      keywords     = 'robotframework testing testautomation selenium selenium2 webdriver web',
      platforms    = 'any',
      classifiers  = [
                        "Development Status :: 5 - Production/Stable",
                        "License :: OSI Approved :: Apache Software License",
                        "Operating System :: OS Independent",
                        "Programming Language :: Python",
                        "Topic :: Software Development :: Testing"
                     ],
      install_requires = [
							'decorator >= 3.3.2',
							'selenium >= 2.32.0',
							'robotframework >= 2.6.0',
							'docutils >= 0.8.1'
						 ],
      py_modules=['ez_setup'],
      package_dir  = {'' : 'src'},
      packages     = ['Selenium2Library','Selenium2Library.keywords','Selenium2Library.locators',
                      'Selenium2Library.utils'],
      include_package_data = True,
      )
