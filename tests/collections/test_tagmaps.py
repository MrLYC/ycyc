#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.collections import tagmaps


class TestTagMaps(TestCase):
    def test_uasge(self):
        maps = tagmaps.TagMaps()

        @maps.register("add")
        def add(x, y):
            return x + y

        @maps.register("sub")
        def sub(x, y):
            return x - y

        self.assertEqual(maps["add"](1, 2), add(1, 2))
        self.assertEqual(maps["sub"](4, 5), sub(4, 5))

        with self.assertRaises(KeyError):
            self.assertEqual(maps["noexist"](6, 7), None)

        @maps.register(maps.DefaultKey)
        def default(x, y):
            return None

        self.assertEqual(maps["noexist"](8, 9), default(8, 9))

        self.assertListEqual(list(maps), ["", "add", "sub"])
        self.assertEqual(list(maps)[0], "")
        self.assertEqual(list(maps)[1], "add")
        self.assertEqual(list(maps)[2], "sub")
