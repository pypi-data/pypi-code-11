# coding: utf-8
"""
    pyextend.core.fieldref
    ~~~~~~~~~~~~~~~~~~~~
    pyextend core fieldref lib

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
from weakref import WeakKeyDictionary


class NonNegative(object):
    """A descriptor that forbids negative values"""
    def __init__(self, default):
        self._default = default
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        # we get here when someone calls x.d, and d is a NonNegative instance
        # instance = x
        # owner = type(x)
        # print('instance', instance)
        # print('owner', owner)
        # print('data', [x for x in self._data.items()])
        return self._data.get(instance, self._default)

    def __set__(self, instance, value):
        # we get here when someone calls x.d, and d is a NonNegative instance
        # instance = x
        # value = val
        if value < 0:
            raise ValueError("Negative value not allowed: {}".format(value))
        self._data[instance] = value
        

if __name__ == '__main__':
    class Person(object):
        age = NonNegative(1)
        score = NonNegative(0)

        def __init__(self, name, age, score):
            self.name = name
            self.age = age
            self.score = score

        def hello(self):
            print("hi, my name is {}, i'm {} years old."
                  .format(self.name, self.age))

    import unittest

    class TestPerson(unittest.TestCase):
       def test_nonnegative(self):
            a = Person('jim', 10, 100)
            self.assertEqual(a.age, 10)
            self.assertEqual(a.score, 100)
            try:
                a.age = -1
            except ValueError:
                self.assertEqual(a.age, 10)


    unittest.main()
