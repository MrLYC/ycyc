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


class TestSimpleExceptions(TestCase):
    def test_usage(self):
        simple_exceptions = typeutils.SimpleExceptions()
        self.assertIsInstance(simple_exceptions.NewError, type)
        self.assertIs(simple_exceptions.NewError, simple_exceptions.NewError)


class TestFreezedAttrs(TestCase):
    def test_usage(self):
        @typeutils.freezed_attrs(["name", "value"])
        class TestObj(object):
            def __init__(self, name, value):
                self.name = name
                self.value = value

        m = TestObj("test", 123)
        with self.assertRaisesRegexp(AttributeError, "name is not writable"):
            m.name = 1
        self.assertEqual(m.name, "test")
        with self.assertRaisesRegexp(AttributeError, "value is not writable"):
            m.value = 1
        self.assertEqual(m.value, 123)
        with self.assertRaisesRegexp(AttributeError, "noting is not writable"):
            m.noting = 1
        self.assertFalse(hasattr(m, "noting"))


class TestConstants(TestCase):
    def test_usage(self):
        const = typeutils.constants(
            Id="TestConstants",
            Name="TestConstants",
            Function="test_usage",
        )

        self.assertIsInstance(const, typeutils.Constants)
        self.assertEqual(const.Id, "TestConstants")  # pylint: disable=E1101
        self.assertEqual(const.Name, "TestConstants")  # pylint: disable=E1101
        self.assertTupleEqual(const["TestConstants"], ("Id", "Name"))
        self.assertEqual(const.Function, "test_usage")  # pylint: disable=E1101
        self.assertTupleEqual(const["test_usage"], ("Function",))
        self.assertIsNone(const["noting"])

        with self.assertRaisesRegexp(
            AttributeError,
            "attribute Name is not writable",
        ):
            const.Name = "error"

        with self.assertRaisesRegexp(
            AttributeError,
            "attribute Function is not writable",
        ):
            const.Function = "error"

        self.assertDictEqual(dict(const), {
            "Id": "TestConstants",
            "Name": "TestConstants",
            "Function": "test_usage",
        })


class TestEnums(TestCase):
    def test_usage(self):
        enums = typeutils.enums("a", "b", "c")

        self.assertEqual(enums.a, 0)  # pylint: disable=E1101
        self.assertEqual(enums.b, 1)  # pylint: disable=E1101
        self.assertEqual(enums.c, 2)  # pylint: disable=E1101

        self.assertEqual(enums[0], "a")
        self.assertEqual(enums[1], "b")
        self.assertEqual(enums[2], "c")

        with self.assertRaisesRegexp(
            AttributeError,
            "attribute a is not writable",
        ):
            enums.a = 2

        self.assertDictEqual(dict(enums), {
            "a": 0, "b": 1, "c": 2,
        })
