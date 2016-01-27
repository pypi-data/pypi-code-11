#!/usr/bin/env python

# pylint: disable=F0401,W0401,W0603,

import os
import sys
import socket
import logging
l = logging.getLogger("claripy")
l.addHandler(logging.NullHandler())

from .errors import *
from . import operations
from . import ops as _all_operations

# This is here for later, because we'll fuck the namespace in a few lines
from . import backends as _backends_module

#
# connect to ANA
#

import ana
if os.environ.get('REMOTE', False):
    ana.set_dl(mongo_args=())

#
# Some other misguided setup
#

_recurse = 15000
l.warning("Claripy is setting the recursion limit to %d. If Python segfaults, I am sorry.", _recurse)
sys.setrecursionlimit(_recurse)

#
# solvers
#

from .frontend import Frontend as _Frontend
from .frontends import LightFrontend, FullFrontend, CompositeFrontend, HybridFrontend, ReplacementFrontend
from .result import Result

#
# backend objects
#

from . import bv
from . import fp
from . import vsa
from .fp import FSORT_DOUBLE, FSORT_FLOAT

#
# Operations
#

from .ast.base import *
from .ast.bv import *
from .ast.fp import *
from .ast.bool import *
from . import ast
del BV
del Bool
del FP
del Base
ast._import()

def BV(name, size, explicit_name=None): #pylint:disable=function-redefined
    l.critical("DEPRECATION WARNING: claripy.BV is deprecated and will soon be removed. Please use claripy.BVS, instead.")
    print "DEPRECATION WARNING: claripy.BV is deprecated and will soon be removed. Please use claripy.BVS, instead."
    return BVS(name, size, explicit_name=explicit_name)

#
# Initialize the backends
#

from . import backend_manager as _backend_manager
_backend_manager.backends._register_backend(_backends_module.BackendConcrete(), 'concrete', True, True)
_backend_manager.backends._register_backend(_backends_module.BackendVSA(), 'vsa', False, False)

if not os.environ.get('WORKER', False) and os.environ.get('REMOTE', False):
    try:
        _backend_z3 = _backends_module.backendremote.BackendRemote()
    except socket.error:
        raise ImportError("can't connect to backend")
else:
    _backend_z3 = _backends_module.BackendZ3()

_backend_manager.backends._register_backend(_backend_z3, 'z3', False, False)
backends = _backend_manager.backends

def downsize():
    backends.downsize()

def Solver():
    return HybridFrontend(backends.z3)
