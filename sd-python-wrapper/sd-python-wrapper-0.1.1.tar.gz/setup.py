#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

# with open('HISTORY.rst') as history_file:
#     history = history_file.read()

requirements = [
    'jsonschema==2.5.1',
    'requests==2.9.1',
    'isodate==0.5.4',
    'pymongo==3.2'
]

test_requirements = [
    'bumpversion==0.5.3',
    'wheel==0.24.0',
    'flake8==2.4.1',
    'tox==2.1.1',
    'coverage==4.0',
    'cryptography==1.0.1',
    'PyYAML==3.11',
]

setup(
    name='sd-python-wrapper',
    version='0.1.1',
    description="A python wrapper for the Server Density Api",
    long_description=readme + '\n\n', # + history,
    author="Jonathan Sundqvist",
    author_email='hello@serverdensity.com',
    url='https://github.com/serverdensity/sd-python-wrapper',
    package_dir={'serverdensity':
                 'serverdensity'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='monitoring,serverdensity',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
