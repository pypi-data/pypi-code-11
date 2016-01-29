#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of django-ca (https://github.com/mathiasertl/django-ca).
#
# django-ca is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# django-ca is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with django-ca.  If not,
# see <http://www.gnu.org/licenses/>.

from distutils.core import setup


long_description = """django-ca provides you with a local TLS certificate authority. It is based on `pyOpenSSL <https://pyopenssl.readthedocs.org/>`_ and `Django <https://www.djangoproject.com/>`_, it can be used as an app in an existing Django project or with the basic project included. Certificates can be managed through Djangos admin interface or via ``manage.py`` commands - no webserver is needed, if you’re happy with the command-line.

Features:

* Set up a secure local certificate authority in just a few minutes.
* Written in Python3.4+.
* Manage your entire certificate authority from the command line and/or via
  Djangos admin interface.
* Get email notifications about certificates about to expire.
* Support for certificate revocation lists (CRLs) and OCSP (both have to be
  hosted separately).

Please see https://django-ca.readthedocs.org for more extensive documentation.
"""

setup(
    name='django-ca',
    version='1.0.0b1',
    description='A Django app providing a SSL/TLS certificate authority.',
    long_description=long_description,
    author='Mathias Ertl',
    author_email='mati@er.tl',
    url='https://github.com/mathiasertl/django-ca',
    packages=[
        'django_ca',
        'django_ca.management',
        'django_ca.management.commands',
        'django_ca.migrations',
    ],
    package_dir={'': 'ca'},
    zip_safe=False,  # because of the static files
    install_requires=[
        'Django>=1.9',
        'pyOpenSSL>=0.15',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 1.9',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Security :: Cryptography',
        'Topic :: Security',
    ],
)
