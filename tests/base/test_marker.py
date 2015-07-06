#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.base import marker


def TestMarker(TestCase):
    def test_usage(self):
        self.assertNotEqual(marker.Marker(), marker.Marker())

        test1 = marker.Marker("test")
        test2 = marker.Marker("test")
        self.assertEqual(test1, test2)
        self.assertIsNot(test1, test2)

        test_undefined = marker.Marker("undefined")
        self.assertEqual(test_undefined, marker.Undefined)
        self.assertIsNot(test_undefined, marker.Undefined)

        marker = marker.Marker()
        self.assertEqual(marker, marker)
        self.assertIs(marker, marker)