#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.base import marker


def TestMarker(TestCase):
    def test_usage(self):
        self.assertNotEqual(marker.Marker(), marker.Marker())
        self.assertNotEqual(marker.Marker("test"), marker.Marker("test"))
        self.assertNotEqual(marker.Marker("undefined"), marker.Undefined)
        marker = marker.Marker()
        self.assertEqual(marker, marker)
        self.assertIs(marker, marker)
