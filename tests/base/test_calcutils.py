#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
from collections import namedtuple

from ycyc.base import calcutils

ObjModel = namedtuple("ObjModel", ["key"])


class TestSafeCalc(TestCase):
    def test_usage(self):
        calc = calcutils.SafeCalc({
            "vint": 1, "vfloat": 2.3, "vstr": "456", "vlist": [7, 8.9, "10"],
            "vdict": {"key1": 11, "key2": ObjModel(key=12.13)}
        })
        self.assertEqual(calc("vint+1"), 2)
        self.assertEqual(calc("0.09 < vfloat/23 < 0.1"), True)
        self.assertEqual(calc("vstr == '456'"), True)
        self.assertEqual(calc("7 in vlist"), True)
        self.assertEqual(set(calc("vdict.keys()")), set(["key1", "key2"]))
        self.assertEqual(calc("vdict['key1']/10 == vint"), True)
        self.assertEqual(calc("12 and 34 or 56"), 34)

    def test_func(self):
        import operator

        calc = calcutils.SafeCalc({
            "add": operator.add, "sub": operator.sub,
        })

        self.assertEqual(calc("add(1, sub(2, 3))"), 0)

        with self.assertRaises(calcutils.NameParseError):
            calc("mul(4, 5)")

        with self.assertRaises(NameError):
            calc("mul")

        self.assert_(issubclass(calcutils.NameParseError, NameError))

    def test_evil(self):
        forbidden_exprs = (
            "import os", "open('test.txt', 'w')", "def x(): pass; print x.func_globals",
            "().__class__.mro()[1].__subclasses__()"
        )
        calc = calcutils.SafeCalc({})

        for e in forbidden_exprs:
            with self.assertRaises(Exception):
                print e
                calc(e)
