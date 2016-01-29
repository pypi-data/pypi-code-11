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
Test version module
"""
from jw.util import version

def test1():
    """
    Test constructor
    """
    v = version.Version('1.0')
    assert v.version == [1, 0]

def test2():
    """
    Test incrementing
    """
    v = version.Version('1.0')
    v.incr()
    assert v.version == [1, 1]

def test3():
    """
    Test incrementing
    """
    v = version.Version('1.0')
    v.decr()
    assert v.version == [1, -1]

def test3():
    """
    Test incrementing at higher level
    """
    v = version.Version('1.0')
    v.incr(-2)
    assert v.version == [2]

def test4():
    "Test __str__()"
    v = version.Version('1.0')
    assert str(v) == '1.0'