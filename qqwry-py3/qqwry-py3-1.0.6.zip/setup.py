#!/usr/bin/env python
import os
from distutils.core import setup

def read_file(path):
    with open(os.path.join(os.path.dirname(__file__), path), encoding='utf-8-sig') as fp:
        return fp.read()

setup(
    name='qqwry-py3',
    version='1.0.6',
    description='Lookup location of IP in qqwry.dat, for Python 3.0+',
    long_description=read_file('qqwry.txt'),
    author='animalize',
    author_email='animalize81@hotmail.com',
    url='https://github.com/animalize/qqwry-python3',
    license='BSD',
    keywords = 'qqwry cz88 纯真 ip归属地',
    platforms=['any'],
    packages=['qqwry'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities'
    ]
)
