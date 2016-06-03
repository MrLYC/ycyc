#!/usr/bin/env python
# encoding: utf-8

import re
from unittest import TestCase

from ycyc.base import resources


class TestRegex(TestCase):
    def pattern_equal_rex(self, pattern):
        return re.compile(pattern.rstrip("$") + "$")

    def test_num_less_than(self):
        with self.assertRaises(ValueError):
            rex = re.compile(resources.Regex.num_less_than(0))

        def test_num(num):
            rex = self.pattern_equal_rex(resources.Regex.num_less_than(num))
            for i in range(num + num / 2):
                if i < num:
                    self.assertIsNotNone(rex.match(str(i)))
                else:
                    self.assertIsNone(rex.match(str(i)))

        test_num(1)
        test_num(2)

        test_num(9)
        test_num(10)
        test_num(11)
        test_num(12)

        test_num(99)
        test_num(100)
        test_num(101)
        test_num(102)

        test_num(200)
        test_num(201)
        test_num(255)
        test_num(256)

        test_num(999)
        test_num(1000)
        test_num(1001)
        test_num(1010)
        test_num(1100)

        test_num(1991)
        test_num(1999)
        test_num(2000)
        test_num(2001)
        test_num(2002)
