"""OpenCL target integrated with PyOpenCL."""

from __future__ import division, absolute_import

__copyright__ = "Copyright (C) 2015 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import six
from six.moves import range

import numpy as np

from loopy.target.opencl import OpenCLTarget

import pyopencl as cl
import pyopencl.characterize as cl_char

# This ensures the dtype registry is populated.
import pyopencl.tools  # noqa

import logging
logger = logging.getLogger(__name__)


# {{{ temp storage adjust for bank conflict

def adjust_local_temp_var_storage(kernel, device):
    logger.debug("%s: adjust temp var storage" % kernel.name)

    new_temp_vars = {}

    lmem_size = cl_char.usable_local_mem_size(device)
    for temp_var in six.itervalues(kernel.temporary_variables):
        if not temp_var.is_local:
            new_temp_vars[temp_var.name] = \
                    temp_var.copy(storage_shape=temp_var.shape)
            continue

        other_loctemp_nbytes = [
                tv.nbytes
                for tv in six.itervalues(kernel.temporary_variables)
                if tv.is_local and tv.name != temp_var.name]

        storage_shape = temp_var.storage_shape

        if storage_shape is None:
            storage_shape = temp_var.shape

        storage_shape = list(storage_shape)

        # sizes of all dims except the last one, which we may change
        # below to avoid bank conflicts
        from pytools import product

        if device.local_mem_type == cl.device_local_mem_type.GLOBAL:
            # FIXME: could try to avoid cache associativity disasters
            new_storage_shape = storage_shape

        elif device.local_mem_type == cl.device_local_mem_type.LOCAL:
            min_mult = cl_char.local_memory_bank_count(device)
            good_incr = None
            new_storage_shape = storage_shape
            min_why_not = None

            for increment in range(storage_shape[-1]//2):

                test_storage_shape = storage_shape[:]
                test_storage_shape[-1] = test_storage_shape[-1] + increment
                new_mult, why_not = cl_char.why_not_local_access_conflict_free(
                        device, temp_var.dtype.itemsize,
                        temp_var.shape, test_storage_shape)

                # will choose smallest increment 'automatically'
                if new_mult < min_mult:
                    new_lmem_use = (sum(other_loctemp_nbytes)
                            + temp_var.dtype.itemsize*product(test_storage_shape))
                    if new_lmem_use < lmem_size:
                        new_storage_shape = test_storage_shape
                        min_mult = new_mult
                        min_why_not = why_not
                        good_incr = increment

            if min_mult != 1:
                from warnings import warn
                from loopy.diagnostic import LoopyAdvisory
                warn("could not find a conflict-free mem layout "
                        "for local variable '%s' "
                        "(currently: %dx conflict, increment: %s, reason: %s)"
                        % (temp_var.name, min_mult, good_incr, min_why_not),
                        LoopyAdvisory)
        else:
            from warnings import warn
            warn("unknown type of local memory")

            new_storage_shape = storage_shape

        new_temp_vars[temp_var.name] = temp_var.copy(storage_shape=new_storage_shape)

    return kernel.copy(temporary_variables=new_temp_vars)

# }}}


# {{{ check sizes against device properties

def check_sizes(kernel, device):
    import loopy as lp

    from loopy.diagnostic import LoopyAdvisory, LoopyError

    if device is None:
        from loopy.diagnostic import warn
        warn(kernel, "no_device_in_pre_codegen_checks",
                "No device parameter was passed to the PyOpenCLTarget. "
                "Perhaps you want to pass a device to benefit from "
                "additional checking.", LoopyAdvisory)
        return

    parameters = {}
    for arg in kernel.args:
        if isinstance(arg, lp.ValueArg) and arg.approximately is not None:
            parameters[arg.name] = arg.approximately

    glens, llens = kernel.get_grid_sizes_as_exprs()

    if (max(len(glens), len(llens))
            > device.max_work_item_dimensions):
        raise LoopyError("too many work item dimensions")

    from pymbolic import evaluate
    from pymbolic.mapper.evaluator import UnknownVariableError
    try:
        glens = evaluate(glens, parameters)
        llens = evaluate(llens, parameters)
    except UnknownVariableError as name:
        from warnings import warn
        warn("could not check axis bounds because no value "
                "for variable '%s' was passed to check_kernels()"
                % name, LoopyAdvisory)
    else:
        for i in range(len(llens)):
            if llens[i] > device.max_work_item_sizes[i]:
                raise LoopyError("group axis %d too big" % i)

        from pytools import product
        if product(llens) > device.max_work_group_size:
            raise LoopyError("work group too big")

    from pyopencl.characterize import usable_local_mem_size
    if kernel.local_mem_use() > usable_local_mem_size(device):
        raise LoopyError("using too much local memory")

    from loopy.kernel.data import ConstantArg
    const_arg_count = sum(
            1 for arg in kernel.args
            if isinstance(arg, ConstantArg))

    if const_arg_count > device.max_constant_args:
        raise LoopyError("too many constant arguments")

# }}}


def pyopencl_function_mangler(target, name, arg_dtypes):
    if len(arg_dtypes) == 1 and isinstance(name, str):
        arg_dtype, = arg_dtypes

        if arg_dtype.kind == "c":
            if arg_dtype == np.complex64:
                tpname = "cfloat"
            elif arg_dtype == np.complex128:
                tpname = "cdouble"
            else:
                raise RuntimeError("unexpected complex type '%s'" % arg_dtype)

            if name in ["sqrt", "exp", "log",
                    "sin", "cos", "tan",
                    "sinh", "cosh", "tanh",
                    "conj"]:
                return arg_dtype, "%s_%s" % (tpname, name)

            if name in ["real", "imag", "abs"]:
                return np.dtype(arg_dtype.type(0).real), "%s_%s" % (tpname, name)

    return None


# {{{ preamble generator

def pyopencl_preamble_generator(target, seen_dtypes, seen_functions):
    has_double = False
    has_complex = False

    for dtype in seen_dtypes:
        if dtype in [np.float64, np.complex128]:
            has_double = True
        if dtype.kind == "c":
            has_complex = True

    if has_complex:
        if has_double:
            yield ("10_include_complex_header", """
                #define PYOPENCL_DEFINE_CDOUBLE

                #include <pyopencl-complex.h>
                """)
        else:
            yield ("10_include_complex_header", """
                #include <pyopencl-complex.h>
                """)

# }}}


# {{{ pyopencl tools

class _LegacyTypeRegistryStub(object):
    """Adapts legacy PyOpenCL type registry to be usable with PyOpenCLTarget."""

    def get_or_register_dtype(self, names, dtype=None):
        from pyopencl.compyte.dtypes import get_or_register_dtype
        return get_or_register_dtype(names, dtype)

    def dtype_to_ctype(self, dtype):
        from pyopencl.compyte.dtypes import dtype_to_ctype
        return dtype_to_ctype(dtype)


class PyOpenCLTarget(OpenCLTarget):
    def __init__(self, device=None):
        super(PyOpenCLTarget, self).__init__()

        self.device = device

    hash_fields = ["device"]
    comparison_fields = ["device"]

    def function_manglers(self):
        return (
                super(PyOpenCLTarget, self).function_manglers() + [
                    pyopencl_function_mangler
                    ])

    def preamble_generators(self):
        return ([
            pyopencl_preamble_generator
            ] + super(PyOpenCLTarget, self).preamble_generators())

    def preprocess(self, kernel):
        return kernel

    def pre_codegen_check(self, kernel):
        check_sizes(kernel, self.device)

    def get_dtype_registry(self):
        try:
            from pyopencl.compyte.dtypes import TYPE_REGISTRY
        except ImportError:
            return _LegacyTypeRegistryStub()
        else:
            return TYPE_REGISTRY

    def is_vector_dtype(self, dtype):
        from pyopencl.array import vec
        return dtype in list(vec.types.values())

    def vector_dtype(self, base, count):
        from pyopencl.array import vec
        return vec.types[base, count]

    def alignment_requirement(self, type_decl):
        import struct

        fmt = (type_decl.struct_format()
                .replace("F", "ff")
                .replace("D", "dd"))

        return struct.calcsize(fmt)

# }}}


# vim: foldmethod=marker
