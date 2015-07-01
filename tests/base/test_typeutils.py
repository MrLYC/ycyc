#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.base import typeutils


class TestSubType(TestCase):
    def test_usage(self):
        self.assertTrue(issubclass(
            typeutils.subtype("Test"),
            object
        ))
        self.assertTrue(issubclass(
            typeutils.subtype("Test", dict),
            dict
        ))
        self.assertTrue(issubclass(
            typeutils.subtype("Test", (dict,)),
            dict
        ))
        TestType = typeutils.subtype("Test", object, {"val": 1})
        self.assertEqual(TestType.__name__, "Test")
        self.assertEqual(TestType.val, 1)
        obj = TestType()
        self.assertEqual(obj.val, 1)


class TestTypesFactory(TestCase):
    def test_usage(self):
        TestType = typeutils.types_factory.TestType()
        self.assertTrue(issubclass(TestType, object))
        self.assertIsNot(TestType, typeutils.types_factory.TestType())
        self.assertTrue(issubclass(
            typeutils.types_factory.TestType(dict),
            dict
        ))
        TestType = typeutils.types_factory.TestType(attrs={"val": 1})
        self.assertEqual(TestType.__name__, "TestType")
        self.assertEqual(TestType.val, 1)
        obj = TestType()
        self.assertEqual(obj.val, 1)


class TestSubException(TestCase):
    def test_usage(self):
        self.assertTrue(issubclass(
            typeutils.subexception("Test"),
            Exception
        ))


class TestExceptionsFactory(TestCase):
    def test_usage(self):
        TestType = typeutils.exceptions_factory.TestType()
        self.assertTrue(issubclass(TestType, Exception))
        self.assertIsNot(TestType, typeutils.exceptions_factory.TestType())
