import unittest

import reflectutils


class Foo(object):
	"""A mock class"""
	def bar(self):
		"""Does nothing"""
		pass


class TypeutilsTest(unittest.TestCase):
	def test_classify(self):
		f = Foo()
		self.assertEqual(reflectutils.classify(f), "object")
		self.assertEqual(reflectutils.classify(Foo), "type")
		self.assertEqual(reflectutils.classify(reflectutils), "module")
		self.assertEqual(reflectutils.classify(Foo.bar), "function")
		self.assertEqual(reflectutils.classify(f.bar), "function")

	def type_fullname_from_str(self):
		s = "<subprocess.Popen at 0x105630bd0>"
		self.assertEqual(reflectutils.fullname_from_str(s), "subprocess.Popen")

		s = "<built-in method search of _sre.SRE_Pattern object at 0x105648558>"
		self.assertEqual(reflectutils.fullname_from_str(s), "_sre.SRE_Pattern.search")

		s = "<method 'search' of '_sre.SRE_Pattern' objects>"
		self.assertEqual(reflectutils.fullname_from_str(s), "_sre.SRE_Pattern.search")

		s = "<method 'flush' of 'file' objects>"
		self.assertEqual(reflectutils.fullname_from_str(s), "__builtin__.file.flush")

		s = "<bound method Popen.kill of <subprocess.Popen object at 0x1056309d0>>"
		self.assertEqual(reflectutils.fullname_from_str(s), "subprocess.Popen.kill")

		s = "<unbound method Popen.kill>"
		self.assertEqual(reflectutils.fullname_from_str(s, pkg="subprocess"), "subprocess.Popen.kill")

	def test_fullname(self):
		f = Foo()
		self.assertEqual(reflectutils.fullname(unittest), "unittest")
		self.assertEqual(reflectutils.fullname(unittest.TestCase), "unittest.case.TestCase")
		self.assertEqual(reflectutils.fullname(unittest.TestCase.assertEqual), "unittest.case.TestCase.assertEqual")
		self.assertEqual(reflectutils.fullname(1), None)

	def test_package(self):
		f = Foo()
		self.assertEqual(reflectutils.package(unittest), "unittest")
		self.assertEqual(reflectutils.package(unittest.TestCase), "unittest.case")
		self.assertEqual(reflectutils.package(unittest.TestCase.assertEqual), "unittest.case")
		self.assertEqual(reflectutils.package(1), None)

	def test_doc(self):
		self.assertEqual(reflectutils.doc(Foo), "A mock class")
		self.assertEqual(reflectutils.doc(Foo.bar), "Does nothing")
