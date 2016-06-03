#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.base import marker


class TestMarker(TestCase):
    def test_usage(self):
        self.assertNotEqual(marker.Marker(), marker.Marker())

        test1 = marker.Marker("test")
        test2 = marker.Marker("test")
        self.assertEqual(test1, test2)
        self.assertIsNot(test1, test2)

        test_undefined = marker.Marker("undefined")
        self.assertEqual(test_undefined, marker.Marker.Undefined)
        self.assertIsNot(test_undefined, marker.Marker.Undefined)

        m = marker.Marker()
        self.assertEqual(m, m)
        self.assertIs(m, m)

        self.assertFalse(bool(marker.Marker.Undefined))
        self.assertFalse(bool(marker.Marker.Missed))
        self.assertFalse(bool(marker.Marker.Disabled))

        m = marker.Marker("test", True)
        self.assertTrue(m)

    def test_freeze_attrs(self):
        m = marker.Marker("test", 123)
        with self.assertRaisesRegexp(AttributeError, "name is not writable"):
            m.name = 1
        self.assertEqual(m.name, "test")
        with self.assertRaisesRegexp(AttributeError, "value is not writable"):
            m.value = 1
        self.assertEqual(m.value, 123)
        with self.assertRaisesRegexp(AttributeError, "has no attribute 'foo'"):
            m.foo = 1  # pylint: disable=E0237
        self.assertFalse(hasattr(m, "foo"))
