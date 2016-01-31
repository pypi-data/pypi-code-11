import codecs

from os import path
from setuptools import find_packages, setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


setup(
    author="Pinax Developers",
    author_email="developers@pinaxproject.com",
    description="framework and base learning activities for Pinax LMS",
    name="pinax-lms-activities",
    long_description=read("README.rst"),
    version="0.5.0",
    url="http://pinax-lms-activities.rtfd.org/",
    license="MIT",
    packages=find_packages(),
    package_data={
        "pinax.lms.activities": [
            "templates/activities/*"
        ]
    },
    test_suite="runtests.runtests",
    install_requires=[
        "pinax-eventlog>=1.1.1",
        "jsonfield>=1.0.3"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
