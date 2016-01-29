# -*- coding: utf-8 -*-
"""Implementation of execution-related magic functions."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function

import ast
import bdb
import gc
import itertools
import os
import sys
import time
import timeit
from pdb import Restart

# cProfile was added in Python2.5
try:
    import cProfile as profile
    import pstats
except ImportError:
    # profile isn't bundled by default in Debian for license reasons
    try:
        import profile, pstats
    except ImportError:
        profile = pstats = None

from IPython.core import debugger, oinspect
from IPython.core import magic_arguments
from IPython.core import page
from IPython.core.error import UsageError
from IPython.core.macro import Macro
from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic,
                                line_cell_magic, on_off, needs_local_scope)
from IPython.testing.skipdoctest import skip_doctest
from IPython.utils import py3compat
from IPython.utils.py3compat import builtin_mod, iteritems, PY3
from IPython.utils.contexts import preserve_keys
from IPython.utils.capture import capture_output
from IPython.utils.ipstruct import Struct
from IPython.utils.module_paths import find_mod
from IPython.utils.path import get_py_filename, unquote_filename, shellglob
from IPython.utils.timing import clock, clock2
from IPython.utils.warn import warn, error

if PY3:
    from io import StringIO
else:
    from StringIO import StringIO

#-----------------------------------------------------------------------------
# Magic implementation classes
#-----------------------------------------------------------------------------


class TimeitResult(object):
    """
    Object returned by the timeit magic with info about the run.

    Contain the following attributes :

    loops: (int) number of loop done per measurement
    repeat: (int) number of time the mesurement has been repeated
    best: (float) best execusion time / number
    all_runs: (list of float) execusion time of each run (in s)
    compile_time: (float) time of statement compilation (s)

    """

    def __init__(self, loops, repeat, best, worst, all_runs, compile_time, precision):
        self.loops = loops
        self.repeat = repeat
        self.best = best
        self.worst = worst
        self.all_runs = all_runs
        self.compile_time = compile_time
        self._precision = precision

    def _repr_pretty_(self, p , cycle):
         if self.loops == 1:  # No s at "loops" if only one loop
             unic =  u"%d loop, best of %d: %s per loop" % (self.loops, self.repeat,
                                            _format_time(self.best, self._precision))
         else:
             unic =  u"%d loops, best of %d: %s per loop" % (self.loops, self.repeat,
                                            _format_time(self.best, self._precision))
         p.text(u'<TimeitResult : '+unic+u'>')


class TimeitTemplateFiller(ast.NodeTransformer):
    """Fill in the AST template for timing execution.

    This is quite closely tied to the template definition, which is in
    :meth:`ExecutionMagics.timeit`.
    """
    def __init__(self, ast_setup, ast_stmt):
        self.ast_setup = ast_setup
        self.ast_stmt = ast_stmt

    def visit_FunctionDef(self, node):
        "Fill in the setup statement"
        self.generic_visit(node)
        if node.name == "inner":
            node.body[:1] = self.ast_setup.body

        return node

    def visit_For(self, node):
        "Fill in the statement to be timed"
        if getattr(getattr(node.body[0], 'value', None), 'id', None) == 'stmt':
            node.body = self.ast_stmt.body
        return node


class Timer(timeit.Timer):
    """Timer class that explicitly uses self.inner
    
    which is an undocumented implementation detail of CPython,
    not shared by PyPy.
    """
    # Timer.timeit copied from CPython 3.4.2
    def timeit(self, number=timeit.default_number):
        """Time 'number' executions of the main statement.

        To be precise, this executes the setup statement once, and
        then returns the time it takes to execute the main statement
        a number of times, as a float measured in seconds.  The
        argument is the number of times through the loop, defaulting
        to one million.  The main statement, the setup statement and
        the timer function to be used are passed to the constructor.
        """
        it = itertools.repeat(None, number)
        gcold = gc.isenabled()
        gc.disable()
        try:
            timing = self.inner(it, self.timer)
        finally:
            if gcold:
                gc.enable()
        return timing


@magics_class
class ExecutionMagics(Magics):
    """Magics related to code execution, debugging, profiling, etc.

    """

    def __init__(self, shell):
        super(ExecutionMagics, self).__init__(shell)
        if profile is None:
            self.prun = self.profile_missing_notice
        # Default execution function used to actually run user code.
        self.default_runner = None

    def profile_missing_notice(self, *args, **kwargs):
        error("""\
The profile module could not be found. It has been removed from the standard
python packages because of its non-free license. To use profiling, install the
python-profiler package from non-free.""")

    @skip_doctest
    @line_cell_magic
    def prun(self, parameter_s='', cell=None):

        """Run a statement through the python code profiler.

        Usage, in line mode:
          %prun [options] statement

        Usage, in cell mode:
          %%prun [options] [statement]
          code...
          code...

        In cell mode, the additional code lines are appended to the (possibly
        empty) statement in the first line.  Cell mode allows you to easily
        profile multiline blocks without having to put them in a separate
        function.

        The given statement (which doesn't require quote marks) is run via the
        python profiler in a manner similar to the profile.run() function.
        Namespaces are internally managed to work correctly; profile.run
        cannot be used in IPython because it makes certain assumptions about
        namespaces which do not hold under IPython.

        Options:

        -l <limit>
          you can place restrictions on what or how much of the
          profile gets printed. The limit value can be:

             * A string: only information for function names containing this string
               is printed.

             * An integer: only these many lines are printed.

             * A float (between 0 and 1): this fraction of the report is printed
               (for example, use a limit of 0.4 to see the topmost 40% only).

          You can combine several limits with repeated use of the option. For
          example, ``-l __init__ -l 5`` will print only the topmost 5 lines of
          information about class constructors.

        -r
          return the pstats.Stats object generated by the profiling. This
          object has all the information about the profile in it, and you can
          later use it for further analysis or in other functions.

        -s <key>
          sort profile by given key. You can provide more than one key
          by using the option several times: '-s key1 -s key2 -s key3...'. The
          default sorting key is 'time'.

          The following is copied verbatim from the profile documentation
          referenced below:

          When more than one key is provided, additional keys are used as
          secondary criteria when the there is equality in all keys selected
          before them.

          Abbreviations can be used for any key names, as long as the
          abbreviation is unambiguous.  The following are the keys currently
          defined:

          ============  =====================
          Valid Arg     Meaning
          ============  =====================
          "calls"       call count
          "cumulative"  cumulative time
          "file"        file name
          "module"      file name
          "pcalls"      primitive call count
          "line"        line number
          "name"        function name
          "nfl"         name/file/line
          "stdname"     standard name
          "time"        internal time
          ============  =====================

          Note that all sorts on statistics are in descending order (placing
          most time consuming items first), where as name, file, and line number
          searches are in ascending order (i.e., alphabetical). The subtle
          distinction between "nfl" and "stdname" is that the standard name is a
          sort of the name as printed, which means that the embedded line
          numbers get compared in an odd way.  For example, lines 3, 20, and 40
          would (if the file names were the same) appear in the string order
          "20" "3" and "40".  In contrast, "nfl" does a numeric compare of the
          line numbers.  In fact, sort_stats("nfl") is the same as
          sort_stats("name", "file", "line").

        -T <filename>
          save profile results as shown on screen to a text
          file. The profile is still shown on screen.

        -D <filename>
          save (via dump_stats) profile statistics to given
          filename. This data is in a format understood by the pstats module, and
          is generated by a call to the dump_stats() method of profile
          objects. The profile is still shown on screen.

        -q
          suppress output to the pager.  Best used with -T and/or -D above.

        If you want to run complete programs under the profiler's control, use
        ``%run -p [prof_opts] filename.py [args to program]`` where prof_opts
        contains profiler specific options as described here.

        You can read the complete documentation for the profile module with::

          In [1]: import profile; profile.help()
        """
        opts, arg_str = self.parse_options(parameter_s, 'D:l:rs:T:q',
                                           list_all=True, posix=False)
        if cell is not None:
            arg_str += '\n' + cell
        arg_str = self.shell.input_splitter.transform_cell(arg_str)
        return self._run_with_profiler(arg_str, opts, self.shell.user_ns)

    def _run_with_profiler(self, code, opts, namespace):
        """
        Run `code` with profiler.  Used by ``%prun`` and ``%run -p``.

        Parameters
        ----------
        code : str
            Code to be executed.
        opts : Struct
            Options parsed by `self.parse_options`.
        namespace : dict
            A dictionary for Python namespace (e.g., `self.shell.user_ns`).

        """

        # Fill default values for unspecified options:
        opts.merge(Struct(D=[''], l=[], s=['time'], T=['']))

        prof = profile.Profile()
        try:
            prof = prof.runctx(code, namespace, namespace)
            sys_exit = ''
        except SystemExit:
            sys_exit = """*** SystemExit exception caught in code being profiled."""

        stats = pstats.Stats(prof).strip_dirs().sort_stats(*opts.s)

        lims = opts.l
        if lims:
            lims = []  # rebuild lims with ints/floats/strings
            for lim in opts.l:
                try:
                    lims.append(int(lim))
                except ValueError:
                    try:
                        lims.append(float(lim))
                    except ValueError:
                        lims.append(lim)

        # Trap output.
        stdout_trap = StringIO()
        stats_stream = stats.stream
        try:
            stats.stream = stdout_trap
            stats.print_stats(*lims)
        finally:
            stats.stream = stats_stream

        output = stdout_trap.getvalue()
        output = output.rstrip()

        if 'q' not in opts:
            page.page(output)
        print(sys_exit, end=' ')

        dump_file = opts.D[0]
        text_file = opts.T[0]
        if dump_file:
            dump_file = unquote_filename(dump_file)
            prof.dump_stats(dump_file)
            print('\n*** Profile stats marshalled to file',\
                  repr(dump_file)+'.',sys_exit)
        if text_file:
            text_file = unquote_filename(text_file)
            pfile = open(text_file,'w')
            pfile.write(output)
            pfile.close()
            print('\n*** Profile printout saved to text file',\
                  repr(text_file)+'.',sys_exit)

        if 'r' in opts:
            return stats
        else:
            return None

    @line_magic
    def pdb(self, parameter_s=''):
        """Control the automatic calling of the pdb interactive debugger.

        Call as '%pdb on', '%pdb 1', '%pdb off' or '%pdb 0'. If called without
        argument it works as a toggle.

        When an exception is triggered, IPython can optionally call the
        interactive pdb debugger after the traceback printout. %pdb toggles
        this feature on and off.

        The initial state of this feature is set in your configuration
        file (the option is ``InteractiveShell.pdb``).

        If you want to just activate the debugger AFTER an exception has fired,
        without having to type '%pdb on' and rerunning your code, you can use
        the %debug magic."""

        par = parameter_s.strip().lower()

        if par:
            try:
                new_pdb = {'off':0,'0':0,'on':1,'1':1}[par]
            except KeyError:
                print ('Incorrect argument. Use on/1, off/0, '
                       'or nothing for a toggle.')
                return
        else:
            # toggle
            new_pdb = not self.shell.call_pdb

        # set on the shell
        self.shell.call_pdb = new_pdb
        print('Automatic pdb calling has been turned',on_off(new_pdb))

    @skip_doctest
    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--breakpoint', '-b', metavar='FILE:LINE',
        help="""
        Set break point at LINE in FILE.
        """
    )
    @magic_arguments.argument('statement', nargs='*',
        help="""
        Code to run in debugger.
        You can omit this in cell magic mode.
        """
    )
    @line_cell_magic
    def debug(self, line='', cell=None):
        """Activate the interactive debugger.

        This magic command support two ways of activating debugger.
        One is to activate debugger before executing code.  This way, you
        can set a break point, to step through the code from the point.
        You can use this mode by giving statements to execute and optionally
        a breakpoint.

        The other one is to activate debugger in post-mortem mode.  You can
        activate this mode simply running %debug without any argument.
        If an exception has just occurred, this lets you inspect its stack
        frames interactively.  Note that this will always work only on the last
        traceback that occurred, so you must call this quickly after an
        exception that you wish to inspect has fired, because if another one
        occurs, it clobbers the previous one.

        If you want IPython to automatically do this on every exception, see
        the %pdb magic for more details.
        """
        args = magic_arguments.parse_argstring(self.debug, line)

        if not (args.breakpoint or args.statement or cell):
            self._debug_post_mortem()
        else:
            code = "\n".join(args.statement)
            if cell:
                code += "\n" + cell
            self._debug_exec(code, args.breakpoint)

    def _debug_post_mortem(self):
        self.shell.debugger(force=True)

    def _debug_exec(self, code, breakpoint):
        if breakpoint:
            (filename, bp_line) = breakpoint.split(':', 1)
            bp_line = int(bp_line)
        else:
            (filename, bp_line) = (None, None)
        self._run_with_debugger(code, self.shell.user_ns, filename, bp_line)

    @line_magic
    def tb(self, s):
        """Print the last traceback with the currently active exception mode.

        See %xmode for changing exception reporting modes."""
        self.shell.showtraceback()

    @skip_doctest
    @line_magic
    def run(self, parameter_s='', runner=None,
                  file_finder=get_py_filename):
        """Run the named file inside IPython as a program.

        Usage::
        
          %run [-n -i -e -G]
               [( -t [-N<N>] | -d [-b<N>] | -p [profile options] )]
               ( -m mod | file ) [args]

        Parameters after the filename are passed as command-line arguments to
        the program (put in sys.argv). Then, control returns to IPython's
        prompt.

        This is similar to running at a system prompt ``python file args``,
        but with the advantage of giving you IPython's tracebacks, and of
        loading all variables into your interactive namespace for further use
        (unless -p is used, see below).

        The file is executed in a namespace initially consisting only of
        ``__name__=='__main__'`` and sys.argv constructed as indicated. It thus
        sees its environment as if it were being run as a stand-alone program
        (except for sharing global objects such as previously imported
        modules). But after execution, the IPython interactive namespace gets
        updated with all variables defined in the program (except for __name__
        and sys.argv). This allows for very convenient loading of code for
        interactive work, while giving each program a 'clean sheet' to run in.

        Arguments are expanded using shell-like glob match.  Patterns
        '*', '?', '[seq]' and '[!seq]' can be used.  Additionally,
        tilde '~' will be expanded into user's home directory.  Unlike
        real shells, quotation does not suppress expansions.  Use
        *two* back slashes (e.g. ``\\\\*``) to suppress expansions.
        To completely disable these expansions, you can use -G flag.

        Options:

        -n
          __name__ is NOT set to '__main__', but to the running file's name
          without extension (as python does under import).  This allows running
          scripts and reloading the definitions in them without calling code
          protected by an ``if __name__ == "__main__"`` clause.

        -i
          run the file in IPython's namespace instead of an empty one. This
          is useful if you are experimenting with code written in a text editor
          which depends on variables defined interactively.

        -e
          ignore sys.exit() calls or SystemExit exceptions in the script
          being run.  This is particularly useful if IPython is being used to
          run unittests, which always exit with a sys.exit() call.  In such
          cases you are interested in the output of the test results, not in
          seeing a traceback of the unittest module.

        -t
          print timing information at the end of the run.  IPython will give
          you an estimated CPU time consumption for your script, which under
          Unix uses the resource module to avoid the wraparound problems of
          time.clock().  Under Unix, an estimate of time spent on system tasks
          is also given (for Windows platforms this is reported as 0.0).

        If -t is given, an additional ``-N<N>`` option can be given, where <N>
        must be an integer indicating how many times you want the script to
        run.  The final timing report will include total and per run results.

        For example (testing the script uniq_stable.py)::

            In [1]: run -t uniq_stable

            IPython CPU timings (estimated):
              User  :    0.19597 s.
              System:        0.0 s.

            In [2]: run -t -N5 uniq_stable

            IPython CPU timings (estimated):
            Total runs performed: 5
              Times :      Total       Per run
              User  :   0.910862 s,  0.1821724 s.
              System:        0.0 s,        0.0 s.

        -d
          run your program under the control of pdb, the Python debugger.
          This allows you to execute your program step by step, watch variables,
          etc.  Internally, what IPython does is similar to calling::

              pdb.run('execfile("YOURFILENAME")')

          with a breakpoint set on line 1 of your file.  You can change the line
          number for this automatic breakpoint to be <N> by using the -bN option
          (where N must be an integer). For example::

              %run -d -b40 myscript

          will set the first breakpoint at line 40 in myscript.py.  Note that
          the first breakpoint must be set on a line which actually does
          something (not a comment or docstring) for it to stop execution.

          Or you can specify a breakpoint in a different file::

              %run -d -b myotherfile.py:20 myscript

          When the pdb debugger starts, you will see a (Pdb) prompt.  You must
          first enter 'c' (without quotes) to start execution up to the first
          breakpoint.

          Entering 'help' gives information about the use of the debugger.  You
          can easily see pdb's full documentation with "import pdb;pdb.help()"
          at a prompt.

        -p
          run program under the control of the Python profiler module (which
          prints a detailed report of execution times, function calls, etc).

          You can pass other options after -p which affect the behavior of the
          profiler itself. See the docs for %prun for details.

          In this mode, the program's variables do NOT propagate back to the
          IPython interactive namespace (because they remain in the namespace
          where the profiler executes them).

          Internally this triggers a call to %prun, see its documentation for
          details on the options available specifically for profiling.

        There is one special usage for which the text above doesn't apply:
        if the filename ends with .ipy[nb], the file is run as ipython script,
        just as if the commands were written on IPython prompt.

        -m
          specify module name to load instead of script path. Similar to
          the -m option for the python interpreter. Use this option last if you
          want to combine with other %run options. Unlike the python interpreter
          only source modules are allowed no .pyc or .pyo files.
          For example::

              %run -m example

          will run the example module.

        -G
          disable shell-like glob expansion of arguments.

        """

        # get arguments and set sys.argv for program to be run.
        opts, arg_lst = self.parse_options(parameter_s,
                                           'nidtN:b:pD:l:rs:T:em:G',
                                           mode='list', list_all=1)
        if "m" in opts:
            modulename = opts["m"][0]
            modpath = find_mod(modulename)
            if modpath is None:
                warn('%r is not a valid modulename on sys.path'%modulename)
                return
            arg_lst = [modpath] + arg_lst
        try:
            filename = file_finder(arg_lst[0])
        except IndexError:
            warn('you must provide at least a filename.')
            print('\n%run:\n', oinspect.getdoc(self.run))
            return
        except IOError as e:
            try:
                msg = str(e)
            except UnicodeError:
                msg = e.message
            error(msg)
            return

        if filename.lower().endswith(('.ipy', '.ipynb')):
            with preserve_keys(self.shell.user_ns, '__file__'):
                self.shell.user_ns['__file__'] = filename
                self.shell.safe_execfile_ipy(filename)
            return

        # Control the response to exit() calls made by the script being run
        exit_ignore = 'e' in opts

        # Make sure that the running script gets a proper sys.argv as if it
        # were run from a system shell.
        save_argv = sys.argv # save it for later restoring

        if 'G' in opts:
            args = arg_lst[1:]
        else:
            # tilde and glob expansion
            args = shellglob(map(os.path.expanduser,  arg_lst[1:]))

        sys.argv = [filename] + args  # put in the proper filename
        # protect sys.argv from potential unicode strings on Python 2:
        if not py3compat.PY3:
            sys.argv = [ py3compat.cast_bytes(a) for a in sys.argv ]

        if 'i' in opts:
            # Run in user's interactive namespace
            prog_ns = self.shell.user_ns
            __name__save = self.shell.user_ns['__name__']
            prog_ns['__name__'] = '__main__'
            main_mod = self.shell.user_module
            
            # Since '%run foo' emulates 'python foo.py' at the cmd line, we must
            # set the __file__ global in the script's namespace
            # TK: Is this necessary in interactive mode?
            prog_ns['__file__'] = filename
        else:
            # Run in a fresh, empty namespace
            if 'n' in opts:
                name = os.path.splitext(os.path.basename(filename))[0]
            else:
                name = '__main__'

            # The shell MUST hold a reference to prog_ns so after %run
            # exits, the python deletion mechanism doesn't zero it out
            # (leaving dangling references). See interactiveshell for details
            main_mod = self.shell.new_main_mod(filename, name)
            prog_ns = main_mod.__dict__

        # pickle fix.  See interactiveshell for an explanation.  But we need to
        # make sure that, if we overwrite __main__, we replace it at the end
        main_mod_name = prog_ns['__name__']

        if main_mod_name == '__main__':
            restore_main = sys.modules['__main__']
        else:
            restore_main = False

        # This needs to be undone at the end to prevent holding references to
        # every single object ever created.
        sys.modules[main_mod_name] = main_mod

        if 'p' in opts or 'd' in opts:
            if 'm' in opts:
                code = 'run_module(modulename, prog_ns)'
                code_ns = {
                    'run_module': self.shell.safe_run_module,
                    'prog_ns': prog_ns,
                    'modulename': modulename,
                }
            else:
                if 'd' in opts:
                    # allow exceptions to raise in debug mode
                    code = 'execfile(filename, prog_ns, raise_exceptions=True)'
                else:
                    code = 'execfile(filename, prog_ns)'
                code_ns = {
                    'execfile': self.shell.safe_execfile,
                    'prog_ns': prog_ns,
                    'filename': get_py_filename(filename),
                }

        try:
            stats = None
            with self.shell.readline_no_record:
                if 'p' in opts:
                    stats = self._run_with_profiler(code, opts, code_ns)
                else:
                    if 'd' in opts:
                        bp_file, bp_line = parse_breakpoint(
                            opts.get('b', ['1'])[0], filename)
                        self._run_with_debugger(
                            code, code_ns, filename, bp_line, bp_file)
                    else:
                        if 'm' in opts:
                            def run():
                                self.shell.safe_run_module(modulename, prog_ns)
                        else:
                            if runner is None:
                                runner = self.default_runner
                            if runner is None:
                                runner = self.shell.safe_execfile

                            def run():
                                runner(filename, prog_ns, prog_ns,
                                       exit_ignore=exit_ignore)

                        if 't' in opts:
                            # timed execution
                            try:
                                nruns = int(opts['N'][0])
                                if nruns < 1:
                                    error('Number of runs must be >=1')
                                    return
                            except (KeyError):
                                nruns = 1
                            self._run_with_timing(run, nruns)
                        else:
                            # regular execution
                            run()

                if 'i' in opts:
                    self.shell.user_ns['__name__'] = __name__save
                else:
                    # update IPython interactive namespace

                    # Some forms of read errors on the file may mean the
                    # __name__ key was never set; using pop we don't have to
                    # worry about a possible KeyError.
                    prog_ns.pop('__name__', None)

                    with preserve_keys(self.shell.user_ns, '__file__'):
                        self.shell.user_ns.update(prog_ns)
        finally:
            # It's a bit of a mystery why, but __builtins__ can change from
            # being a module to becoming a dict missing some key data after
            # %run.  As best I can see, this is NOT something IPython is doing
            # at all, and similar problems have been reported before:
            # http://coding.derkeiler.com/Archive/Python/comp.lang.python/2004-10/0188.html
            # Since this seems to be done by the interpreter itself, the best
            # we can do is to at least restore __builtins__ for the user on
            # exit.
            self.shell.user_ns['__builtins__'] = builtin_mod

            # Ensure key global structures are restored
            sys.argv = save_argv
            if restore_main:
                sys.modules['__main__'] = restore_main
            else:
                # Remove from sys.modules the reference to main_mod we'd
                # added.  Otherwise it will trap references to objects
                # contained therein.
                del sys.modules[main_mod_name]

        return stats

    def _run_with_debugger(self, code, code_ns, filename=None,
                           bp_line=None, bp_file=None):
        """
        Run `code` in debugger with a break point.

        Parameters
        ----------
        code : str
            Code to execute.
        code_ns : dict
            A namespace in which `code` is executed.
        filename : str
            `code` is ran as if it is in `filename`.
        bp_line : int, optional
            Line number of the break point.
        bp_file : str, optional
            Path to the file in which break point is specified.
            `filename` is used if not given.

        Raises
        ------
        UsageError
            If the break point given by `bp_line` is not valid.

        """
        deb = debugger.Pdb(self.shell.colors)
        # reset Breakpoint state, which is moronically kept
        # in a class
        bdb.Breakpoint.next = 1
        bdb.Breakpoint.bplist = {}
        bdb.Breakpoint.bpbynumber = [None]
        if bp_line is not None:
            # Set an initial breakpoint to stop execution
            maxtries = 10
            bp_file = bp_file or filename
            checkline = deb.checkline(bp_file, bp_line)
            if not checkline:
                for bp in range(bp_line + 1, bp_line + maxtries + 1):
                    if deb.checkline(bp_file, bp):
                        break
                else:
                    msg = ("\nI failed to find a valid line to set "
                           "a breakpoint\n"
                           "after trying up to line: %s.\n"
                           "Please set a valid breakpoint manually "
                           "with the -b option." % bp)
                    raise UsageError(msg)
            # if we find a good linenumber, set the breakpoint
            deb.do_break('%s:%s' % (bp_file, bp_line))

        if filename:
            # Mimic Pdb._runscript(...)
            deb._wait_for_mainpyfile = True
            deb.mainpyfile = deb.canonic(filename)

        # Start file run
        print("NOTE: Enter 'c' at the %s prompt to continue execution." % deb.prompt)
        try:
            if filename:
                # save filename so it can be used by methods on the deb object
                deb._exec_filename = filename
            while True:
                try:
                    deb.run(code, code_ns)
                except Restart:
                    print("Restarting")
                    if filename:
                        deb._wait_for_mainpyfile = True
                        deb.mainpyfile = deb.canonic(filename)
                    continue
                else:
                    break
            

        except:
            etype, value, tb = sys.exc_info()
            # Skip three frames in the traceback: the %run one,
            # one inside bdb.py, and the command-line typed by the
            # user (run by exec in pdb itself).
            self.shell.InteractiveTB(etype, value, tb, tb_offset=3)

    @staticmethod
    def _run_with_timing(run, nruns):
        """
        Run function `run` and print timing information.

        Parameters
        ----------
        run : callable
            Any callable object which takes no argument.
        nruns : int
            Number of times to execute `run`.

        """
        twall0 = time.time()
        if nruns == 1:
            t0 = clock2()
            run()
            t1 = clock2()
            t_usr = t1[0] - t0[0]
            t_sys = t1[1] - t0[1]
            print("\nIPython CPU timings (estimated):")
            print("  User   : %10.2f s." % t_usr)
            print("  System : %10.2f s." % t_sys)
        else:
            runs = range(nruns)
            t0 = clock2()
            for nr in runs:
                run()
            t1 = clock2()
            t_usr = t1[0] - t0[0]
            t_sys = t1[1] - t0[1]
            print("\nIPython CPU timings (estimated):")
            print("Total runs performed:", nruns)
            print("  Times  : %10s   %10s" % ('Total', 'Per run'))
            print("  User   : %10.2f s, %10.2f s." % (t_usr, t_usr / nruns))
            print("  System : %10.2f s, %10.2f s." % (t_sys, t_sys / nruns))
        twall1 = time.time()
        print("Wall time: %10.2f s." % (twall1 - twall0))

    @skip_doctest
    @line_cell_magic
    def timeit(self, line='', cell=None):
        """Time execution of a Python statement or expression

        Usage, in line mode:
          %timeit [-n<N> -r<R> [-t|-c] -q -p<P> -o] statement
        or in cell mode:
          %%timeit [-n<N> -r<R> [-t|-c] -q -p<P> -o] setup_code
          code
          code...

        Time execution of a Python statement or expression using the timeit
        module.  This function can be used both as a line and cell magic:

        - In line mode you can time a single-line statement (though multiple
          ones can be chained with using semicolons).

        - In cell mode, the statement in the first line is used as setup code
          (executed but not timed) and the body of the cell is timed.  The cell
          body has access to any variables created in the setup code.

        Options:
        -n<N>: execute the given statement <N> times in a loop. If this value
        is not given, a fitting value is chosen.

        -r<R>: repeat the loop iteration <R> times and take the best result.
        Default: 3

        -t: use time.time to measure the time, which is the default on Unix.
        This function measures wall time.

        -c: use time.clock to measure the time, which is the default on
        Windows and measures wall time. On Unix, resource.getrusage is used
        instead and returns the CPU user time.

        -p<P>: use a precision of <P> digits to display the timing result.
        Default: 3

        -q: Quiet, do not print result.

        -o: return a TimeitResult that can be stored in a variable to inspect
            the result in more details.


        Examples
        --------
        ::

          In [1]: %timeit pass
          10000000 loops, best of 3: 53.3 ns per loop

          In [2]: u = None

          In [3]: %timeit u is None
          10000000 loops, best of 3: 184 ns per loop

          In [4]: %timeit -r 4 u == None
          1000000 loops, best of 4: 242 ns per loop

          In [5]: import time

          In [6]: %timeit -n1 time.sleep(2)
          1 loop, best of 3: 2 s per loop


        The times reported by %timeit will be slightly higher than those
        reported by the timeit.py script when variables are accessed. This is
        due to the fact that %timeit executes the statement in the namespace
        of the shell, compared with timeit.py, which uses a single setup
        statement to import function or create variables. Generally, the bias
        does not matter as long as results from timeit.py are not mixed with
        those from %timeit."""

        opts, stmt = self.parse_options(line,'n:r:tcp:qo',
                                        posix=False, strict=False)
        if stmt == "" and cell is None:
            return
        
        timefunc = timeit.default_timer
        number = int(getattr(opts, "n", 0))
        repeat = int(getattr(opts, "r", timeit.default_repeat))
        precision = int(getattr(opts, "p", 3))
        quiet = 'q' in opts
        return_result = 'o' in opts
        if hasattr(opts, "t"):
            timefunc = time.time
        if hasattr(opts, "c"):
            timefunc = clock

        timer = Timer(timer=timefunc)
        # this code has tight coupling to the inner workings of timeit.Timer,
        # but is there a better way to achieve that the code stmt has access
        # to the shell namespace?
        transform  = self.shell.input_splitter.transform_cell

        if cell is None:
            # called as line magic
            ast_setup = self.shell.compile.ast_parse("pass")
            ast_stmt = self.shell.compile.ast_parse(transform(stmt))
        else:
            ast_setup = self.shell.compile.ast_parse(transform(stmt))
            ast_stmt = self.shell.compile.ast_parse(transform(cell))

        ast_setup = self.shell.transform_ast(ast_setup)
        ast_stmt = self.shell.transform_ast(ast_stmt)

        # This codestring is taken from timeit.template - we fill it in as an
        # AST, so that we can apply our AST transformations to the user code
        # without affecting the timing code.
        timeit_ast_template = ast.parse('def inner(_it, _timer):\n'
                                        '    setup\n'
                                        '    _t0 = _timer()\n'
                                        '    for _i in _it:\n'
                                        '        stmt\n'
                                        '    _t1 = _timer()\n'
                                        '    return _t1 - _t0\n')

        timeit_ast = TimeitTemplateFiller(ast_setup, ast_stmt).visit(timeit_ast_template)
        timeit_ast = ast.fix_missing_locations(timeit_ast)

        # Track compilation time so it can be reported if too long
        # Minimum time above which compilation time will be reported
        tc_min = 0.1

        t0 = clock()
        code = self.shell.compile(timeit_ast, "<magic-timeit>", "exec")
        tc = clock()-t0

        ns = {}
        exec(code, self.shell.user_ns, ns)
        timer.inner = ns["inner"]

        # This is used to check if there is a huge difference between the
        # best and worst timings.
        # Issue: https://github.com/ipython/ipython/issues/6471
        worst_tuning = 0
        if number == 0:
            # determine number so that 0.2 <= total time < 2.0
            number = 1
            for _ in range(1, 10):
                time_number = timer.timeit(number)
                worst_tuning = max(worst_tuning, time_number / number)
                if time_number >= 0.2:
                    break
                number *= 10
        all_runs = timer.repeat(repeat, number)
        best = min(all_runs) / number

        worst = max(all_runs) / number
        if worst_tuning:
            worst = max(worst, worst_tuning)

        if not quiet :
            # Check best timing is greater than zero to avoid a
            # ZeroDivisionError.
            # In cases where the slowest timing is lesser than a micosecond
            # we assume that it does not really matter if the fastest
            # timing is 4 times faster than the slowest timing or not.
            if worst > 4 * best and best > 0 and worst > 1e-6:
                print("The slowest run took %0.2f times longer than the "
                      "fastest. This could mean that an intermediate result "
                      "is being cached." % (worst / best))
            if number == 1:  # No s at "loops" if only one loop
                print(u"%d loop, best of %d: %s per loop" % (number, repeat,
                                                              _format_time(best, precision)))
            else:
                print(u"%d loops, best of %d: %s per loop" % (number, repeat,
                                                              _format_time(best, precision)))
            if tc > tc_min:
                print("Compiler time: %.2f s" % tc)
        if return_result:
            return TimeitResult(number, repeat, best, worst, all_runs, tc, precision)

    @skip_doctest
    @needs_local_scope
    @line_cell_magic
    def time(self,line='', cell=None, local_ns=None):
        """Time execution of a Python statement or expression.

        The CPU and wall clock times are printed, and the value of the
        expression (if any) is returned.  Note that under Win32, system time
        is always reported as 0, since it can not be measured.
        
        This function can be used both as a line and cell magic:

        - In line mode you can time a single-line statement (though multiple
          ones can be chained with using semicolons).

        - In cell mode, you can time the cell body (a directly 
          following statement raises an error).

        This function provides very basic timing functionality.  Use the timeit 
        magic for more control over the measurement.

        Examples
        --------
        ::

          In [1]: %time 2**128
          CPU times: user 0.00 s, sys: 0.00 s, total: 0.00 s
          Wall time: 0.00
          Out[1]: 340282366920938463463374607431768211456L

          In [2]: n = 1000000

          In [3]: %time sum(range(n))
          CPU times: user 1.20 s, sys: 0.05 s, total: 1.25 s
          Wall time: 1.37
          Out[3]: 499999500000L

          In [4]: %time print 'hello world'
          hello world
          CPU times: user 0.00 s, sys: 0.00 s, total: 0.00 s
          Wall time: 0.00

          Note that the time needed by Python to compile the given expression
          will be reported if it is more than 0.1s.  In this example, the
          actual exponentiation is done by Python at compilation time, so while
          the expression can take a noticeable amount of time to compute, that
          time is purely due to the compilation:

          In [5]: %time 3**9999;
          CPU times: user 0.00 s, sys: 0.00 s, total: 0.00 s
          Wall time: 0.00 s

          In [6]: %time 3**999999;
          CPU times: user 0.00 s, sys: 0.00 s, total: 0.00 s
          Wall time: 0.00 s
          Compiler : 0.78 s
          """

        # fail immediately if the given expression can't be compiled
        
        if line and cell:
            raise UsageError("Can't use statement directly after '%%time'!")
        
        if cell:
            expr = self.shell.input_transformer_manager.transform_cell(cell)
        else:
            expr = self.shell.input_transformer_manager.transform_cell(line)

        # Minimum time above which parse time will be reported
        tp_min = 0.1

        t0 = clock()
        expr_ast = self.shell.compile.ast_parse(expr)
        tp = clock()-t0

        # Apply AST transformations
        expr_ast = self.shell.transform_ast(expr_ast)

        # Minimum time above which compilation time will be reported
        tc_min = 0.1

        if len(expr_ast.body)==1 and isinstance(expr_ast.body[0], ast.Expr):
            mode = 'eval'
            source = '<timed eval>'
            expr_ast = ast.Expression(expr_ast.body[0].value)
        else:
            mode = 'exec'
            source = '<timed exec>'
        t0 = clock()
        code = self.shell.compile(expr_ast, source, mode)
        tc = clock()-t0

        # skew measurement as little as possible
        glob = self.shell.user_ns
        wtime = time.time
        # time execution
        wall_st = wtime()
        if mode=='eval':
            st = clock2()
            out = eval(code, glob, local_ns)
            end = clock2()
        else:
            st = clock2()
            exec(code, glob, local_ns)
            end = clock2()
            out = None
        wall_end = wtime()
        # Compute actual times and report
        wall_time = wall_end-wall_st
        cpu_user = end[0]-st[0]
        cpu_sys = end[1]-st[1]
        cpu_tot = cpu_user+cpu_sys
        # On windows cpu_sys is always zero, so no new information to the next print 
        if sys.platform != 'win32':
            print("CPU times: user %s, sys: %s, total: %s" % \
                (_format_time(cpu_user),_format_time(cpu_sys),_format_time(cpu_tot)))
        print("Wall time: %s" % _format_time(wall_time))
        if tc > tc_min:
            print("Compiler : %s" % _format_time(tc))
        if tp > tp_min:
            print("Parser   : %s" % _format_time(tp))
        return out

    @skip_doctest
    @line_magic
    def macro(self, parameter_s=''):
        """Define a macro for future re-execution. It accepts ranges of history,
        filenames or string objects.

        Usage:\\
          %macro [options] name n1-n2 n3-n4 ... n5 .. n6 ...

        Options:

          -r: use 'raw' input.  By default, the 'processed' history is used,
          so that magics are loaded in their transformed version to valid
          Python.  If this option is given, the raw input as typed at the
          command line is used instead.
          
          -q: quiet macro definition.  By default, a tag line is printed 
          to indicate the macro has been created, and then the contents of 
          the macro are printed.  If this option is given, then no printout
          is produced once the macro is created.

        This will define a global variable called `name` which is a string
        made of joining the slices and lines you specify (n1,n2,... numbers
        above) from your input history into a single string. This variable
        acts like an automatic function which re-executes those lines as if
        you had typed them. You just type 'name' at the prompt and the code
        executes.

        The syntax for indicating input ranges is described in %history.

        Note: as a 'hidden' feature, you can also use traditional python slice
        notation, where N:M means numbers N through M-1.

        For example, if your history contains (print using %hist -n )::

          44: x=1
          45: y=3
          46: z=x+y
          47: print x
          48: a=5
          49: print 'x',x,'y',y

        you can create a macro with lines 44 through 47 (included) and line 49
        called my_macro with::

          In [55]: %macro my_macro 44-47 49

        Now, typing `my_macro` (without quotes) will re-execute all this code
        in one pass.

        You don't need to give the line-numbers in order, and any given line
        number can appear multiple times. You can assemble macros with any
        lines from your input history in any order.

        The macro is a simple object which holds its value in an attribute,
        but IPython's display system checks for macros and executes them as
        code instead of printing them when you type their name.

        You can view a macro's contents by explicitly printing it with::

          print macro_name

        """
        opts,args = self.parse_options(parameter_s,'rq',mode='list')
        if not args:   # List existing macros
            return sorted(k for k,v in iteritems(self.shell.user_ns) if\
                                                        isinstance(v, Macro))
        if len(args) == 1:
            raise UsageError(
                "%macro insufficient args; usage '%macro name n1-n2 n3-4...")
        name, codefrom = args[0], " ".join(args[1:])

        #print 'rng',ranges  # dbg
        try:
            lines = self.shell.find_user_code(codefrom, 'r' in opts)
        except (ValueError, TypeError) as e:
            print(e.args[0])
            return
        macro = Macro(lines)
        self.shell.define_macro(name, macro)
        if not ( 'q' in opts) : 
            print('Macro `%s` created. To execute, type its name (without quotes).' % name)
            print('=== Macro contents: ===')
            print(macro, end=' ')

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('output', type=str, default='', nargs='?',
        help="""The name of the variable in which to store output.
        This is a utils.io.CapturedIO object with stdout/err attributes
        for the text of the captured output.

        CapturedOutput also has a show() method for displaying the output,
        and __call__ as well, so you can use that to quickly display the
        output.

        If unspecified, captured output is discarded.
        """
    )
    @magic_arguments.argument('--no-stderr', action="store_true",
        help="""Don't capture stderr."""
    )
    @magic_arguments.argument('--no-stdout', action="store_true",
        help="""Don't capture stdout."""
    )
    @magic_arguments.argument('--no-display', action="store_true",
        help="""Don't capture IPython's rich display."""
    )
    @cell_magic
    def capture(self, line, cell):
        """run the cell, capturing stdout, stderr, and IPython's rich display() calls."""
        args = magic_arguments.parse_argstring(self.capture, line)
        out = not args.no_stdout
        err = not args.no_stderr
        disp = not args.no_display
        with capture_output(out, err, disp) as io:
            self.shell.run_cell(cell)
        if args.output:
            self.shell.user_ns[args.output] = io

def parse_breakpoint(text, current_file):
    '''Returns (file, line) for file:line and (current_file, line) for line'''
    colon = text.find(':')
    if colon == -1:
        return current_file, int(text)
    else:
        return text[:colon], int(text[colon+1:])
    
def _format_time(timespan, precision=3):
    """Formats the timespan in a human readable form"""
    import math
    
    if timespan >= 60.0:
        # we have more than a minute, format that in a human readable form
        # Idea from http://snipplr.com/view/5713/
        parts = [("d", 60*60*24),("h", 60*60),("min", 60), ("s", 1)]
        time = []
        leftover = timespan
        for suffix, length in parts:
            value = int(leftover / length)
            if value > 0:
                leftover = leftover % length
                time.append(u'%s%s' % (str(value), suffix))
            if leftover < 1:
                break
        return " ".join(time)

    
    # Unfortunately the unicode 'micro' symbol can cause problems in
    # certain terminals.  
    # See bug: https://bugs.launchpad.net/ipython/+bug/348466
    # Try to prevent crashes by being more secure than it needs to
    # E.g. eclipse is able to print a µ, but has no sys.stdout.encoding set.
    units = [u"s", u"ms",u'us',"ns"] # the save value   
    if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
        try:
            u'\xb5'.encode(sys.stdout.encoding)
            units = [u"s", u"ms",u'\xb5s',"ns"]
        except:
            pass
    scaling = [1, 1e3, 1e6, 1e9]
        
    if timespan > 0.0:
        order = min(-int(math.floor(math.log10(timespan)) // 3), 3)
    else:
        order = 3
    return u"%.*g %s" % (precision, timespan * scaling[order], units[order])
