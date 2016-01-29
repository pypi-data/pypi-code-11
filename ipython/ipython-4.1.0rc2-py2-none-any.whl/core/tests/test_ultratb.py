# encoding: utf-8
"""Tests for IPython.core.ultratb
"""
import io
import sys
import os.path
from textwrap import dedent
import traceback
import unittest

try:
    from unittest import mock
except ImportError:
    import mock    # Python 2

from ..ultratb import ColorTB, VerboseTB, find_recursion


from IPython.testing import tools as tt
from IPython.testing.decorators import onlyif_unicode_paths
from IPython.utils.syspathcontext import prepended_to_syspath
from IPython.utils.tempdir import TemporaryDirectory
from IPython.utils.py3compat import PY3

ip = get_ipython()

file_1 = """1
2
3
def f():
  1/0
"""

file_2 = """def f():
  1/0
"""

class ChangedPyFileTest(unittest.TestCase):
    def test_changing_py_file(self):
        """Traceback produced if the line where the error occurred is missing?
        
        https://github.com/ipython/ipython/issues/1456
        """
        with TemporaryDirectory() as td:
            fname = os.path.join(td, "foo.py")
            with open(fname, "w") as f:
                f.write(file_1)
            
            with prepended_to_syspath(td):
                ip.run_cell("import foo")
            
            with tt.AssertPrints("ZeroDivisionError"):
                ip.run_cell("foo.f()")
            
            # Make the file shorter, so the line of the error is missing.
            with open(fname, "w") as f:
                f.write(file_2)
            
            # For some reason, this was failing on the *second* call after
            # changing the file, so we call f() twice.
            with tt.AssertNotPrints("Internal Python error", channel='stderr'):
                with tt.AssertPrints("ZeroDivisionError"):
                    ip.run_cell("foo.f()")
                with tt.AssertPrints("ZeroDivisionError"):
                    ip.run_cell("foo.f()")

iso_8859_5_file = u'''# coding: iso-8859-5

def fail():
    """дбИЖ"""
    1/0     # дбИЖ
'''

class NonAsciiTest(unittest.TestCase):
    @onlyif_unicode_paths
    def test_nonascii_path(self):
        # Non-ascii directory name as well.
        with TemporaryDirectory(suffix=u'é') as td:
            fname = os.path.join(td, u"fooé.py")
            with open(fname, "w") as f:
                f.write(file_1)
            
            with prepended_to_syspath(td):
                ip.run_cell("import foo")
            
            with tt.AssertPrints("ZeroDivisionError"):
                ip.run_cell("foo.f()")
    
    def test_iso8859_5(self):
        with TemporaryDirectory() as td:
            fname = os.path.join(td, 'dfghjkl.py')

            with io.open(fname, 'w', encoding='iso-8859-5') as f:
                f.write(iso_8859_5_file)
            
            with prepended_to_syspath(td):
                ip.run_cell("from dfghjkl import fail")
            
            with tt.AssertPrints("ZeroDivisionError"):
                with tt.AssertPrints(u'дбИЖ', suppress=False):
                    ip.run_cell('fail()')


class NestedGenExprTestCase(unittest.TestCase):
    """
    Regression test for the following issues:
    https://github.com/ipython/ipython/issues/8293
    https://github.com/ipython/ipython/issues/8205
    """
    def test_nested_genexpr(self):
        code = dedent(
            """\
            class SpecificException(Exception):
                pass

            def foo(x):
                raise SpecificException("Success!")

            sum(sum(foo(x) for _ in [0]) for x in [0])
            """
        )
        with tt.AssertPrints('SpecificException: Success!', suppress=False):
            ip.run_cell(code)


indentationerror_file = """if True:
zoon()
"""

class IndentationErrorTest(unittest.TestCase):
    def test_indentationerror_shows_line(self):
        # See issue gh-2398
        with tt.AssertPrints("IndentationError"):
            with tt.AssertPrints("zoon()", suppress=False):
                ip.run_cell(indentationerror_file)
        
        with TemporaryDirectory() as td:
            fname = os.path.join(td, "foo.py")
            with open(fname, "w") as f:
                f.write(indentationerror_file)
            
            with tt.AssertPrints("IndentationError"):
                with tt.AssertPrints("zoon()", suppress=False):
                    ip.magic('run %s' % fname)

se_file_1 = """1
2
7/
"""

se_file_2 = """7/
"""

class SyntaxErrorTest(unittest.TestCase):
    def test_syntaxerror_without_lineno(self):
        with tt.AssertNotPrints("TypeError"):
            with tt.AssertPrints("line unknown"):
                ip.run_cell("raise SyntaxError()")

    def test_changing_py_file(self):
        with TemporaryDirectory() as td:
            fname = os.path.join(td, "foo.py")
            with open(fname, 'w') as f:
                f.write(se_file_1)

            with tt.AssertPrints(["7/", "SyntaxError"]):
                ip.magic("run " + fname)

            # Modify the file
            with open(fname, 'w') as f:
                f.write(se_file_2)

            # The SyntaxError should point to the correct line
            with tt.AssertPrints(["7/", "SyntaxError"]):
                ip.magic("run " + fname)

    def test_non_syntaxerror(self):
        # SyntaxTB may be called with an error other than a SyntaxError
        # See e.g. gh-4361
        try:
            raise ValueError('QWERTY')
        except ValueError:
            with tt.AssertPrints('QWERTY'):
                ip.showsyntaxerror()


class Python3ChainedExceptionsTest(unittest.TestCase):
    DIRECT_CAUSE_ERROR_CODE = """
try:
    x = 1 + 2
    print(not_defined_here)
except Exception as e:
    x += 55
    x - 1
    y = {}
    raise KeyError('uh') from e
    """

    EXCEPTION_DURING_HANDLING_CODE = """
try:
    x = 1 + 2
    print(not_defined_here)
except Exception as e:
    x += 55
    x - 1
    y = {}
    raise KeyError('uh')
    """

    SUPPRESS_CHAINING_CODE = """
try:
    1/0
except Exception:
    raise ValueError("Yikes") from None
    """

    def test_direct_cause_error(self):
        if PY3:
            with tt.AssertPrints(["KeyError", "NameError", "direct cause"]):
                ip.run_cell(self.DIRECT_CAUSE_ERROR_CODE)

    def test_exception_during_handling_error(self):
        if PY3:
            with tt.AssertPrints(["KeyError", "NameError", "During handling"]):
                ip.run_cell(self.EXCEPTION_DURING_HANDLING_CODE)

    def test_suppress_exception_chaining(self):
        if PY3:
            with tt.AssertNotPrints("ZeroDivisionError"), \
                    tt.AssertPrints("ValueError", suppress=False):
                ip.run_cell(self.SUPPRESS_CHAINING_CODE)


class RecursionTest(unittest.TestCase):
    DEFINITIONS = """
def non_recurs():
    1/0

def r1():
    r1()

def r3a():
    r3b()

def r3b():
    r3c()

def r3c():
    r3a()

def r3o1():
    r3a()

def r3o2():
    r3o1()
"""
    def setUp(self):
        ip.run_cell(self.DEFINITIONS)

    def test_no_recursion(self):
        with tt.AssertNotPrints("frames repeated"):
            ip.run_cell("non_recurs()")

    def test_recursion_one_frame(self):
        with tt.AssertPrints("1 frames repeated"):
            ip.run_cell("r1()")

    def test_recursion_three_frames(self):
        with tt.AssertPrints("3 frames repeated"):
            ip.run_cell("r3o2()")

    def test_find_recursion(self):
        captured = []
        def capture_exc(*args, **kwargs):
            captured.append(sys.exc_info())
        with mock.patch.object(ip, 'showtraceback', capture_exc):
            ip.run_cell("r3o2()")

        self.assertEqual(len(captured), 1)
        etype, evalue, tb = captured[0]
        self.assertIn("recursion", str(evalue))

        records = ip.InteractiveTB.get_records(tb, 3, ip.InteractiveTB.tb_offset)
        for r in records[:10]:
            print(r[1:4])

        # The outermost frames should be:
        # 0: the 'cell' that was running when the exception came up
        # 1: r3o2()
        # 2: r3o1()
        # 3: r3a()
        # Then repeating r3b, r3c, r3a
        last_unique, repeat_length = find_recursion(etype, evalue, records)
        self.assertEqual(last_unique, 2)
        self.assertEqual(repeat_length, 3)


#----------------------------------------------------------------------------

# module testing (minimal)
if sys.version_info > (3,):
    def test_handlers():
        def spam(c, d_e):
            (d, e) = d_e
            x = c + d
            y = c * d
            foo(x, y)

        def foo(a, b, bar=1):
            eggs(a, b + bar)

        def eggs(f, g, z=globals()):
            h = f + g
            i = f - g
            return h / i
        
        buff = io.StringIO()

        buff.write('')
        buff.write('*** Before ***')
        try:
            buff.write(spam(1, (2, 3)))
        except:
            traceback.print_exc(file=buff)

        handler = ColorTB(ostream=buff)
        buff.write('*** ColorTB ***')
        try:
            buff.write(spam(1, (2, 3)))
        except:
            handler(*sys.exc_info())
        buff.write('')

        handler = VerboseTB(ostream=buff)
        buff.write('*** VerboseTB ***')
        try:
            buff.write(spam(1, (2, 3)))
        except:
            handler(*sys.exc_info())
        buff.write('')

