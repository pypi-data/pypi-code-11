# encoding: utf-8
"""
IPython: tools for interactive and parallel computing in Python.

http://ipython.org
"""
#-----------------------------------------------------------------------------
#  Copyright (c) 2008-2011, IPython Development Team.
#  Copyright (c) 2001-2007, Fernando Perez <fernando.perez@colorado.edu>
#  Copyright (c) 2001, Janko Hauser <jhauser@zscout.de>
#  Copyright (c) 2001, Nathaniel Gray <n8gray@caltech.edu>
#
#  Distributed under the terms of the Modified BSD License.
#
#  The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import absolute_import

import os
import sys
import warnings

#-----------------------------------------------------------------------------
# Setup everything
#-----------------------------------------------------------------------------

# Don't forget to also update setup.py when this changes!
v = sys.version_info
if v[:2] < (2,7) or (v[0] >= 3 and v[:2] < (3,3)):
    raise ImportError('IPython requires Python version 2.7 or 3.3 or above.')
del v

# Make it easy to import extensions - they are always directly on pythonpath.
# Therefore, non-IPython modules can be added to extensions directory.
# This should probably be in ipapp.py.
sys.path.append(os.path.join(os.path.dirname(__file__), "extensions"))

#-----------------------------------------------------------------------------
# Setup the top level names
#-----------------------------------------------------------------------------

from .core.getipython import get_ipython
from .core import release
from .core.application import Application
from .terminal.embed import embed

from .core.interactiveshell import InteractiveShell
from .testing import test
from .utils.sysinfo import sys_info
from .utils.frame import extract_module_locals

# Release data
__author__ = '%s <%s>' % (release.author, release.author_email)
__license__  = release.license
__version__  = release.version
version_info = release.version_info

def embed_kernel(module=None, local_ns=None, **kwargs):
    """Embed and start an IPython kernel in a given scope.
    
    If you don't want the kernel to initialize the namespace
    from the scope of the surrounding function,
    and/or you want to load full IPython configuration,
    you probably want `IPython.start_kernel()` instead.
    
    Parameters
    ----------
    module : ModuleType, optional
        The module to load into IPython globals (default: caller)
    local_ns : dict, optional
        The namespace to load into IPython user namespace (default: caller)
    
    kwargs : various, optional
        Further keyword args are relayed to the IPKernelApp constructor,
        allowing configuration of the Kernel.  Will only have an effect
        on the first embed_kernel call for a given process.
    """
    
    (caller_module, caller_locals) = extract_module_locals(1)
    if module is None:
        module = caller_module
    if local_ns is None:
        local_ns = caller_locals
    
    # Only import .zmq when we really need it
    from ipykernel.embed import embed_kernel as real_embed_kernel
    real_embed_kernel(module=module, local_ns=local_ns, **kwargs)

def start_ipython(argv=None, **kwargs):
    """Launch a normal IPython instance (as opposed to embedded)
    
    `IPython.embed()` puts a shell in a particular calling scope,
    such as a function or method for debugging purposes,
    which is often not desirable.
    
    `start_ipython()` does full, regular IPython initialization,
    including loading startup files, configuration, etc.
    much of which is skipped by `embed()`.
    
    This is a public API method, and will survive implementation changes.
    
    Parameters
    ----------
    
    argv : list or None, optional
        If unspecified or None, IPython will parse command-line options from sys.argv.
        To prevent any command-line parsing, pass an empty list: `argv=[]`.
    user_ns : dict, optional
        specify this dictionary to initialize the IPython user namespace with particular values.
    kwargs : various, optional
        Any other kwargs will be passed to the Application constructor,
        such as `config`.
    """
    from IPython.terminal.ipapp import launch_new_instance
    return launch_new_instance(argv=argv, **kwargs)

def start_kernel(argv=None, **kwargs):
    """Launch a normal IPython kernel instance (as opposed to embedded)
    
    `IPython.embed_kernel()` puts a shell in a particular calling scope,
    such as a function or method for debugging purposes,
    which is often not desirable.
    
    `start_kernel()` does full, regular IPython initialization,
    including loading startup files, configuration, etc.
    much of which is skipped by `embed()`.
    
    Parameters
    ----------
    
    argv : list or None, optional
        If unspecified or None, IPython will parse command-line options from sys.argv.
        To prevent any command-line parsing, pass an empty list: `argv=[]`.
    user_ns : dict, optional
        specify this dictionary to initialize the IPython user namespace with particular values.
    kwargs : various, optional
        Any other kwargs will be passed to the Application constructor,
        such as `config`.
    """
    from IPython.kernel.zmq.kernelapp import launch_new_instance
    return launch_new_instance(argv=argv, **kwargs)
    
# deprecated shim for IPython.Config
import traitlets.config
class Config(traitlets.config.Config):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "IPython.Config is deprecated and will be removed in IPython 5."
            " Use traitlets.config.Config.",
            DeprecationWarning, stacklevel=2,
        )
        super(Config, self).__init__(*args, **kwargs)

