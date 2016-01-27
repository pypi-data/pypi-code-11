from .bits import Bits
from ..ast.base import _make_name

class FP(Bits):
    def to_fp(self, rm, sort):
        if rm is None:
            rm = fp.RM.default()

        return fpToFP(rm, self, sort)

    def raw_to_fp(self):
        return self

    def to_bv(self):
        return fpToIEEEBV(self)

    @property
    def sort(self):
        return fp.FSort.from_size(self.length)

def FPS(name, sort, explicit_name=None):
    '''
    Creates a floating-point symbol.

    @param name: the name of the symbol
    @param sort: the sort of the floating point
    @param explicit_name: if False, an identifier is appended to the name to ensure
                          uniqueness.

    @return an FP AST
    '''

    n = _make_name(name, sort.length, False if explicit_name is None else explicit_name, prefix='FP_')
    return FP('FP', (n, sort), variables={n}, symbolic=True, length=sort.length)

def FPV(value, sort):
    '''
    Creates a concrete floating-point value.

    @param value: the value of the floating point
    @param sort: the sort of the floating point
    @return an FP AST
    '''
    return FP('FPV', (value, sort), length=sort.length)

#
# unbound floating point conversions
#

from .. import operations
from .. import fp
from .bv import BV
from .bool import Bool

def _fp_length_calc(a1, a2, a3=None):
    if isinstance(a1, fp.RM) and a3 is None:
        raise Exception()
    if a3 is None:
        return a2.length
    else:
        return a3.length

fpToFP = operations.op('fpToFP', object, FP, bound=False, calc_length=_fp_length_calc)
fpToFPUnsigned = operations.op('fpToFPUnsigned', (fp.RM, BV, fp.FSort), FP, bound=False, calc_length=_fp_length_calc)
fpFP = operations.op('fpFP', (BV, BV, BV), FP, bound=False,
                  calc_length=lambda a, b, c: a.length + b.length + c.length)
fpToIEEEBV = operations.op('fpToIEEEBV', (FP,), BV, bound=False, calc_length=lambda fp: fp.length)
fpToSBV = operations.op('fpToSBV', (fp.RM, FP, (int, long)), BV, bound=False, calc_length=lambda _rm, _fp, len: len)
fpToUBV = operations.op('fpToUBV', (fp.RM, FP, (int, long)), BV, bound=False, calc_length=lambda _rm, _fp, len: len)

#
# unbound float point comparisons
#

def _fp_cmp_check(a, b):
    return a.length == b.length, "FP lengths must be the same"
fpEQ = operations.op('fpEQ', (FP, FP), Bool, bound=False, extra_check=_fp_cmp_check)
fpGT = operations.op('fpGT', (FP, FP), Bool, bound=False, extra_check=_fp_cmp_check)
fpGEQ = operations.op('fpGEQ', (FP, FP), Bool, bound=False, extra_check=_fp_cmp_check)
fpLT = operations.op('fpLT', (FP, FP), Bool, bound=False, extra_check=_fp_cmp_check)
fpLEQ = operations.op('fpLEQ', (FP, FP), Bool, bound=False, extra_check=_fp_cmp_check)

#
# unbound floating point arithmetic
#

def _fp_binop_check(rm, a, b): #pylint:disable=unused-argument
    return a.length == b.length, "Lengths must be equal"
def _fp_binop_length(rm, a, b): #pylint:disable=unused-argument
    return a.length
fpAbs = operations.op('fpAbs', (FP,), FP, bound=False, calc_length=lambda x: x.length)
fpNeg = operations.op('fpNeg', (FP,), FP, bound=False, calc_length=lambda x: x.length)
fpSub = operations.op('fpSub', (fp.RM, FP, FP), FP, bound=False, extra_check=_fp_binop_check, calc_length=_fp_binop_length)
fpAdd = operations.op('fpAdd', (fp.RM, FP, FP), FP, bound=False, extra_check=_fp_binop_check, calc_length=_fp_binop_length)
fpMul = operations.op('fpMul', (fp.RM, FP, FP), FP, bound=False, extra_check=_fp_binop_check, calc_length=_fp_binop_length)
fpDiv = operations.op('fpDiv', (fp.RM, FP, FP), FP, bound=False, extra_check=_fp_binop_check, calc_length=_fp_binop_length)

#
# bound fp operations
#
FP.__eq__ = operations.op('fpEQ', (FP, FP), Bool, extra_check=_fp_cmp_check)
FP.__ne__ = operations.op('fpNE', (FP, FP), Bool, extra_check=_fp_cmp_check)
FP.__ge__ = operations.op('fpGEQ', (FP, FP), Bool, extra_check=_fp_cmp_check)
FP.__le__ = operations.op('fpLEQ', (FP, FP), Bool, extra_check=_fp_cmp_check)
FP.__gt__ = operations.op('fpGT', (FP, FP), Bool, extra_check=_fp_cmp_check)
FP.__lt__ = operations.op('fpLT', (FP, FP), Bool, extra_check=_fp_cmp_check)
