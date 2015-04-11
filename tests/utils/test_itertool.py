#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
from collections import namedtuple

from ycyc.utils.itertool import getitems, getattrs


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
