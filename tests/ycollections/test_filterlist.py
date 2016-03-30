#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.ycollections import filterlist


class TestFilterList(TestCase):
    def test_usage(self):
        list1 = filterlist.FilterList(range(5))
        list2 = list1.filter(lambda x: x % 2)
        list3 = list1.exclude(lambda x: x % 2)

        self.assertIsInstance(list2, filterlist.FilterList)
        self.assertIsInstance(list3, filterlist.FilterList)
        self.assertEqual(list(list2), [1, 3])
        self.assertEqual(list(list3), [0, 2, 4])
        self.assertEqual(list1.first(), 0)
        self.assertEqual(list1.last(), 4)

        list1.clear()
        self.assertEqual(list1.first(), None)
        self.assertEqual(list1.last(), None)
        self.assertEqual(list1.first(0), 0)
        self.assertEqual(list1.last(0), 0)
