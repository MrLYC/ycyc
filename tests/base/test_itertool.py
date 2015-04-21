#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
from collections import namedtuple

from ycyc.base.itertool import (
    getitems, getattrs, iterable, getnext, getfirst
)


class Testgetitems(TestCase):
    def test_usage(self):
        model = {
            "key": "test",
            "value": {
                "items": [
                    {
                        "name": "a",
                        "value": 1
                    },
                    {
                        "name": "b",
                        "value": 2
                    }
                ]
            }
        }

        self.assertEqual(getitems(model, "key"), "test")
        self.assertEqual(getitems(model, ["value", "items", 0, "name"]), "a")
        self.assertEqual(getitems(model, ["value", "items", 1, "value"]), 2)
        self.assertEqual(getitems(model, ["value", "items", 2, "value"]), None)
        self.assertEqual(getitems(model, ["value", "items", 3, "value"], 4), 4)


class Testgetattrs(TestCase):
    Pair = namedtuple("Pair", ["key", "value"])

    def test_usage(self):
        Pair = self.Pair
        model = Pair(
            key="test",
            value=Pair(key="a", value=1)
        )

        self.assertEqual(getattrs(model, "key"), "test")
        self.assertEqual(getattrs(model, ["value", "key"]), "a")
        self.assertEqual(getattrs(model, ["value", "value"]), 1)
        self.assertEqual(getattrs(model, ["value", "items"]), None)
        self.assertEqual(getattrs(model, ["value", "items"], 4), 4)


class TestIterObj(TestCase):
    def test_iterable(self):
        self.assertFalse(iterable(object()))
        self.assertTrue(iterable(list()))
        self.assertTrue(iterable(tuple()))
        self.assertTrue(iterable(set()))
        self.assertTrue(iterable(dict()))
        self.assertTrue(iterable(i for i in range(0)))

    def test_getfirst(self):
        self.assertEqual(getfirst(range(5)), 0)
        self.assertEqual(getfirst({"a": 1}), "a")

        gen = (i for i in range(1))
        self.assertEqual(getfirst(gen), 0)
        with self.assertRaises(StopIteration):
            next(gen)

        self.assertEqual(getfirst(None), None)
        self.assertEqual(getfirst([]), None)
        self.assertEqual(getfirst([], 0), 0)

    def test_getnext(self):
        gen = (i for i in range(2))
        self.assertEqual(getnext(gen), 0)
        self.assertEqual(getnext(gen), 1)
        self.assertEqual(getnext(gen), None)
        self.assertEqual(getnext(gen, 2), 2)
