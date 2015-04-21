#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
import six

from ycyc.base import encode, decode


class TestCoding(TestCase):
    def test_encode(self):
        self.assertEqual(decode(u"刘奕聪".encode("utf-8"), "utf-8"), u"刘奕聪")
        self.assertEqual(decode(u"刘奕聪", "utf-8"), u"刘奕聪")
