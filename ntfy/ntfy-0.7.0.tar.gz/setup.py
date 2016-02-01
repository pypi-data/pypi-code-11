from setuptools import setup
from subprocess import check_output, CalledProcessError
from sys import platform
from os import environ

deps = ['requests', 'sleekxmpp', 'emoji']
if platform == 'win32':
    deps.append('pypiwin32')
test_deps = ['mock']

try:
    version_output = check_output(['git', 'describe',
                                   '--match=v*.*.*', '--dirty'])
except (OSError, CalledProcessError):
    version = None
else:
    version_parts = version_output.decode().strip().lstrip('v').split('-')
    if len(version_parts) == 1:
        version = version_parts[0]
    elif len(version_parts) > 1:
        version = '-'.join(version_parts[:2])
    if version_parts[-1] == 'dirty':
        version += '.dev'


setup(
    name='ntfy',

    version=version,

    description='A utility for sending push notifications',

    url='https://github.com/dschep/ntfy',

    author='Daniel Schep',
    author_email='dschep@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Environment :: Console',

        'Intended Audience :: End Users/Desktop',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='push notification',

    packages=['ntfy', 'ntfy.backends'],
    package_data={'ntfy': ['icon.png', 'icon.ico']},

    install_requires=deps,

    tests_require=test_deps,
    test_suite='tests',

    entry_points={
        'console_scripts': [
            'ntfy = ntfy.cli:main',
        ],
    },
)
