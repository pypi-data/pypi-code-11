# -*- coding: utf-8 -*-
"""
Tests of LibraryUsageLocator
"""
import ddt
from bson.objectid import ObjectId
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import UsageKey
from opaque_keys.edx.locator import LibraryUsageLocator, BlockUsageLocator, LibraryLocator
from opaque_keys.edx.tests import LocatorBaseTest

BLOCK_PREFIX = BlockUsageLocator.BLOCK_PREFIX
BLOCK_TYPE_PREFIX = BlockUsageLocator.BLOCK_TYPE_PREFIX
VERSION_PREFIX = BlockUsageLocator.VERSION_PREFIX


@ddt.ddt
class TestLibraryUsageLocators(LocatorBaseTest):
    """
    Tests of :class:`.LibraryUsageLocator`
    """
    @ddt.data(
        u"lib-block-v1:org+lib+{}@category+{}@name".format(BLOCK_TYPE_PREFIX, BLOCK_PREFIX),
        u"lib-block-v1:org+lib+{}@519665f6223ebd6980884f2b+{}@category+{}@name".format(VERSION_PREFIX,
                                                                                       BLOCK_TYPE_PREFIX, BLOCK_PREFIX),
        u"lib-block-v1:org+lib+{}@revision+{}@category+{}@name".format(LibraryLocator.BRANCH_PREFIX, BLOCK_TYPE_PREFIX,
                                                                       BLOCK_PREFIX),
    )
    def test_string_roundtrip(self, url):
        self.assertEquals(
            url,
            unicode(UsageKey.from_string(url))
        )

    @ddt.data(
        ("TestX", "lib3", "html", "html17"),
        (u"ΩmegaX", u"Ωμέγα", u"html", u"html15"),
    )
    @ddt.unpack
    def test_constructor(self, org, lib, block_type, block_id):
        lib_key = LibraryLocator(org=org, library=lib)
        lib_usage_key = LibraryUsageLocator(library_key=lib_key, block_type=block_type, block_id=block_id)
        lib_usage_key2 = UsageKey.from_string(u"lib-block-v1:{}+{}+{}@{}+{}@{}".format(
            org, lib,
            BLOCK_TYPE_PREFIX, block_type,
            BLOCK_PREFIX, block_id
        ))
        self.assertEquals(lib_usage_key, lib_usage_key2)
        self.assertEquals(lib_usage_key.library_key, lib_key)
        self.assertEquals(lib_usage_key.library_key, lib_key)
        self.assertEquals(lib_usage_key.branch, None)
        self.assertEquals(lib_usage_key.run, LibraryLocator.RUN)
        self.assertIsInstance(lib_usage_key2, LibraryUsageLocator)
        self.assertIsInstance(lib_usage_key2.library_key, LibraryLocator)

    def test_no_deprecated_support(self):
        lib_key = LibraryLocator(org="TestX", library="problem-bank-15")
        with self.assertRaises(InvalidKeyError):
            LibraryUsageLocator(library_key=lib_key, block_type="html", block_id="html1", deprecated=True)

    @ddt.data(
        {'block_type': 'html', 'block_id': ''},
        {'block_type': '', 'block_id': 'html15'},
        {'block_type': '+$%@', 'block_id': 'html15'},
        {'block_type': 'html', 'block_id': '+$%@'},
    )
    def test_constructor_invalid(self, kwargs):
        lib_key = LibraryLocator(org="TestX", library="problem-bank-15")
        with self.assertRaises(InvalidKeyError):
            LibraryUsageLocator(library_key=lib_key, **kwargs)

    @ddt.data(
        "lib-block-v1:org+lib+{}@category".format(BLOCK_TYPE_PREFIX),
    )
    def test_constructor_invalid_from_string(self, url):
        with self.assertRaises(InvalidKeyError):
            UsageKey.from_string(url)

    def test_superclass_make_relative(self):
        lib_key = LibraryLocator(org="TestX", library="problem-bank-15")
        obj = BlockUsageLocator.make_relative(lib_key, "block_type", "block_id")
        self.assertIsInstance(obj, LibraryUsageLocator)

    def test_replace(self):
        # pylint: disable=no-member
        org1, lib1, block_type1, block_id1 = "org1", "lib1", "type1", "id1"
        lib_key1 = LibraryLocator(org=org1, library=lib1)
        usage1 = LibraryUsageLocator(library_key=lib_key1, block_type=block_type1, block_id=block_id1)
        self.assertEqual(usage1.org, org1)
        self.assertEqual(usage1.library_key, lib_key1)

        org2, lib2 = "org2", "lib2"
        lib_key2 = LibraryLocator(org=org2, library=lib2)
        usage2 = usage1.replace(library_key=lib_key2)
        self.assertEqual(usage2.library_key, lib_key2)
        self.assertEqual(usage2.course_key, lib_key2)
        self.assertEqual(usage2.block_type, block_type1)  # Unchanged
        self.assertEqual(usage2.block_id, block_id1)  # Unchanged

        block_id3 = "id3"
        lib3 = "lib3"
        usage3 = usage1.replace(block_id=block_id3, library=lib3)
        self.assertEqual(usage3.library_key.org, org1)
        self.assertEqual(usage3.library_key.library, lib3)
        self.assertEqual(usage2.block_type, block_type1)  # Unchanged
        self.assertEqual(usage3.block_id, block_id3)

        lib_key4 = LibraryLocator(org="org4", library="lib4")
        usage4 = usage1.replace(course_key=lib_key4)
        self.assertEqual(usage4.library_key, lib_key4)
        self.assertEqual(usage4.course_key, lib_key4)
        self.assertEqual(usage4.block_type, block_type1)  # Unchanged
        self.assertEqual(usage4.block_id, block_id1)  # Unchanged

        usage5a = usage1.replace(version='aaaaaaaaaaaaaaaaaaaaaaaa')
        usage5b = usage1.replace(version_guid=ObjectId('bbbbbbbbbbbbbbbbbbbbbbbb'))
        usage5c = usage1.for_version(ObjectId('cccccccccccccccccccccccc'))
        self.assertEqual(usage5a.library_key.version_guid, ObjectId('aaaaaaaaaaaaaaaaaaaaaaaa'))
        self.assertEqual(usage5b.course_key.version_guid, ObjectId('bbbbbbbbbbbbbbbbbbbbbbbb'))
        self.assertEqual(usage5c.version_guid, ObjectId('cccccccccccccccccccccccc'))
        self.assertEqual(usage5a.block_type, block_type1)  # Unchanged
        self.assertEqual(usage5a.block_id, block_id1)  # Unchanged
        self.assertEqual(usage5b.block_type, block_type1)  # Unchanged
        self.assertEqual(usage5b.block_id, block_id1)  # Unchanged
        self.assertEqual(usage5c.block_type, block_type1)  # Unchanged
        self.assertEqual(usage5c.block_id, block_id1)  # Unchanged

        usage6 = usage5a.version_agnostic()
        self.assertEqual(usage6, usage1)

        usage7 = usage1.for_branch('tribble')
        self.assertEqual(usage7.branch, 'tribble')
        self.assertEqual(usage7.library_key.branch, 'tribble')

    def test_lib_usage_locator_no_deprecated_support(self):
        with self.assertRaises(NotImplementedError):
            LibraryUsageLocator._from_deprecated_string("1/2/3")  # pylint: disable=protected-access

        lib_key = LibraryLocator(org="TestX", library="lib")
        usage = LibraryUsageLocator(library_key=lib_key, block_type="html", block_id="123")
        with self.assertRaises(NotImplementedError):
            usage._to_deprecated_string()  # pylint: disable=protected-access

        with self.assertRaises(NotImplementedError):
            LibraryUsageLocator._from_deprecated_son("", "")  # pylint: disable=protected-access

        with self.assertRaises(NotImplementedError):
            usage.to_deprecated_son()
