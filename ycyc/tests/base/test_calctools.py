#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
from collections import namedtuple
from textwrap import dedent

import mock

from ycyc.base import calctools

ObjModel = namedtuple("ObjModel", ["key"])


class TestSafeCalc(TestCase):
    def test_usage(self):
        calc = calctools.SafeCalc({
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

        calc = calctools.SafeCalc({
            "add": operator.add, "sub": operator.sub,
        })

        self.assertEqual(calc("add(1, sub(2, 3))"), 0)

        with self.assertRaises(calctools.NameParseError):
            calc("mul(4, 5)")

        with self.assertRaises(NameError):
            calc("mul")

        self.assert_(issubclass(calctools.NameParseError, NameError))

    def test_evil(self):
        forbidden_exprs = (
            "import os", "open('test.txt', 'w')", "def x(): pass; print x.func_globals",
            "().__class__.mro()[1].__subclasses__()"
        )
        calc = calctools.SafeCalc({})

        for e in forbidden_exprs:
            with self.assertRaises(Exception):
                print e
                calc(e)

    def test_timeout(self):
        import time

        calc = calctools.SafeCalc(
            {"sleep": time.sleep},
            timeout=0.05, interval=0.001,
        )
        try:
            calc("sleep(1)")
            self.assertTrue(False)
        except KeyboardInterrupt:
            pass
        except RuntimeError:
            pass

        with self.assertRaisesRegexp(SyntaxError, "invalid syntax"):
            calc("while True: pass")

    def test_allow_attr(self):
        m = mock.MagicMock()
        m.value = 1

        calc = calctools.SafeCalc({"model": m})
        self.assertEqual(calc("model.value + 1"), 2)

        calc = calctools.SafeCalc(
            {"model": m, "value": m.value}, allow_attr=False
        )
        with self.assertRaisesRegexp(NameError, "value not allow"):
            calc("model.value + 1")
        self.assertEqual(calc("value + 1"), 2)


class TesstSafeCalcFunc(TestCase):
    def test_usage(self):
        self.assertEqual(calctools.safecalc("1+1"), 2)
        self.assertEqual(calctools.safecalc("1+a", a=1), 2)
        self.assertEqual(calctools.safecalc("1+a", dict(a=1)), 2)
        self.assertEqual(calctools.safecalc("1+a", dict(a=1), a=2), 3)


class TestSelect(TestCase):
    def test_usage(self):
        obj = {
            "key": {"name": "test"},
            "value": [123],
        }
        self.assertDictEqual(
            calctools.select(obj, ("key", "name"), ("value", 0)),
            {0: obj["key"]["name"], 1: obj["value"][0]}
        )
        self.assertDictEqual(
            calctools.select(obj, key=("key", "name"), value=("value", 0)),
            {"key": obj["key"]["name"], "value": obj["value"][0]}
        )
        self.assertDictEqual(
            calctools.select(obj, noting=("key", "noting")),
            {"noting": None}
        )
