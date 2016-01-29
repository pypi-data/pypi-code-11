# Copyright 2014 Johnny Wezel
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
Test configuration module
"""
import io
import os
import tempfile
import unittest
from nose.tools import eq_
from six import StringIO

from jw.util import configuration

CONFIG1 = """
level1:
    level2:
        str: string
        int: 1
"""

YAML_FILE_NAME = '/tmp/some.yaml'

CONFIG2 = """
- !include {filename}
""".format(filename=YAML_FILE_NAME)

CONFIG_SOME_YAML = """
-
    name: value
    other:
        - 22
        - 33
"""


def test1():
    """
    Test FromString()
    """
    c = configuration.FromString(CONFIG1)
    assert isinstance(c, configuration.Dict)
    assert c['level1']

def test2():
    """
    Test FromStream()
    """
    c = configuration.FromStream(StringIO(CONFIG1))
    assert c['level1']

def test3():
    """
    Test FromFile()
    """
    filename = os.path.join(os.path.sep, 'tmp', '%s.tmp' % __name__)
    open(filename, 'w').write(CONFIG1)
    c = configuration.FromFile(filename)
    assert c['level1']
    os.remove(filename)

def test4():
    """
    Test at()
    """
    c = configuration.FromString(CONFIG1)
    assert c.at('level1.level2.str') == 'string'
    assert c.at('level1.level2.int') == 1
    assert c.at('level1.level2.nothing') is None
    assert c.at('level1.level2.nothing', default='none') == 'none'
    assert c.at('level1.level2.nothing', 'none') == 'none'

def test5():
    """
    Test multi-level path access
    """
    c = configuration.FromString(CONFIG1)
    assert c('level1', 'level2', 'str') == 'string'
    assert c('level1', 'level2', 'nothing', default='none') == 'none'

def test6():
    """
    Test setting item
    """
    c = configuration.Dict()
    c['this'] = 'that'
    assert c('this') == 'that'

def test8():
    """
    Test delete item
    """
    c = configuration.FromString(CONFIG1)
    item = c['level1']['level2']
    del item['str']
    assert c('level1', 'level2', 'str', default='NOT-THERE') is 'NOT-THERE'

def test9():
    """
    Test delete item
    """
    c = configuration.FromString(CONFIG1)
    c.delete('level1', 'level2', 'str')
    assert c('level1', 'level2', 'str', default='NOT-THERE') is 'NOT-THERE'

def test10():
    """
    Test delete item on top level
    """
    c = configuration.FromString(CONFIG1)
    c.delete('level1')
    assert c('level1', default='NOT-THERE') == 'NOT-THERE'

def test11():
    """
    Test attribute access
    """
    c = configuration.FromString(CONFIG1)
    assert isinstance(c.level1, configuration.Dict)
    assert isinstance(c.level1.level2, configuration.Dict)
    eq_(c.level1.level2.str, 'string')

class TestToFile(unittest.TestCase):
    """
    Test configuration.ToFile
    """

    def setUp(self):
        self.filename = tempfile.mktemp()

    def tearDown(self):
        os.remove(self.filename)

    def test1(self):
        c = configuration.Dict()
        c['x'] = 1
        configuration.ToFile(c, self.filename, False)
        c2 = configuration.FromFile(self.filename)
        self.assertEqual(c2['x'], 1)

class TestInclusion(unittest.TestCase):
    """
    Test file inclusion
    """

    def setUp(self):
        open(YAML_FILE_NAME, 'w').write(CONFIG_SOME_YAML)

    def tearDown(self):
        os.remove(YAML_FILE_NAME)

    def test1(self):
        got = configuration.FromString(CONFIG2)
        expected = [[{'name': 'value', 'other': [22, 33]}]]
        assert got == expected, got