#
# This file is part of ToolRack.
#
# ToolRack is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# ToolRack is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ToolRack.  If not, see <http://www.gnu.org/licenses/>.

from io import StringIO
from argparse import ArgumentParser

from unittest import TestCase

from ..script import ErrorExitMessage, Script


class DummyScript(Script):

    called = False
    code = None
    args = None
    failure = None

    def get_parser(self):
        parser = ArgumentParser()
        parser.add_argument('--foo', type=int)
        return parser

    def main(self, args):
        self.called = True
        self.args = args
        if self.failure is not None:
            raise self.failure

    def _exit(self, code):
        self.code = code


class ErrorExitMessageTests(TestCase):

    def test_message(self):
        '''ErrorExitMessage provides a message and a default code.'''
        message = 'Something went wrong!'
        error = ErrorExitMessage(message)
        self.assertEqual(error.message, message)
        self.assertEqual(str(error), message)
        self.assertEqual(error.code, 1)

    def test_code(self):
        '''ErrorExitMessage can provide a different error code.'''
        error = ErrorExitMessage('Something went wrong!', code=3)
        self.assertEqual(error.code, 3)


class ScriptTests(TestCase):

    def setUp(self):
        super().setUp()
        self.stderr = StringIO()
        self.script = DummyScript(stderr=self.stderr)

    def test_call_runs_main(self):
        '''When a Script is called, the main method is executed.'''
        self.script([])
        self.assertTrue(self.script.called)
        self.assertIsNone(self.script.code)

    def test_call_parse_args(self):
        '''When a Script is called, get_parser parses the arguments.'''
        self.script(['--foo', '3'])
        self.assertEqual(self.script.args.foo, 3)
        self.assertEqual(self.stderr.getvalue(), '')

    def test_failure(self):
        '''If ErrorExitMessage is raised, the script is terminated.'''
        self.script.failure = ErrorExitMessage('Fail!', code=3)
        self.script([])
        self.assertEqual(self.stderr.getvalue(), 'Fail!\n')
        self.assertEqual(self.script.code, 3)

    def test_exit(self):
        '''Script.exit exits the process with 0 as return code.'''
        calls = []
        self.script._exit = calls.append
        self.script.exit()
        self.assertEqual(calls, [0])

    def test_exit_with_code(self):
        '''Script.exit exits the process with the specified return code.'''
        calls = []
        self.script._exit = calls.append
        self.script.exit(code=4)
        self.assertEqual(calls, [4])

    def test_handle_keyboard_interrupt(self):
        '''Script.handle_keyboard_interrupt exits cleanly by default.'''
        calls = []
        self.script._exit = calls.append
        self.script.handle_keyboard_interrupt(KeyboardInterrupt())
        self.assertEqual(calls, [0])

    def test_handle_keyboard_interrupt_called(self):
        '''Script.handle_keyboard_interrupt is called on KeyboardInterrupt.'''
        interrupt = KeyboardInterrupt()
        calls = []
        self.script.failure = interrupt
        self.script.handle_keyboard_interrupt = calls.append
        self.script([])
        self.assertEqual(calls, [interrupt])
