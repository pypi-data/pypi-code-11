# pyinfra
# File: pyinfra/facts/pip.py
# Desc: facts for the pip package manager

from pyinfra.api import FactBase

from .util.packaging import parse_packages


class PipPackages(FactBase):
    '''
    Returns a dict of installed pip packages:

    .. code:: python

        'package_name': 'version',
        ...
    '''

    command = 'pip freeze'
    _regex = r'^([a-zA-Z0-9_\-\+\.]+)==([0-9\.]+[a-z0-9\-]*)$'

    process = lambda self, output: parse_packages(self._regex, output)


class PipPackagesVirtualenv(PipPackages):
    def command(self, venv):
        # Remove any trailing slash
        venv = venv.rstrip('/')
        return '{0}/bin/pip freeze'.format(venv)
