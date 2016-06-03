#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
from collections import namedtuple
import operator

from ycyc.base.iterutils import (
    getitems, getattrs, iterable, getnext, getfirst, groupby, mkparts,
    get_single_item, dict_merge, flatten, find_peak_item,
    filter_n, every_n, iter_chunk, safe_max, safe_min,
)

import mock


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


class TestGroupBy(TestCase):
    def test_usage(self):
        data = [
            {"name": "int", "val": 1},
            {"name": "float", "val": 2.3},
            {"name": "float", "val": 4.5},
            {"name": "int", "val": 6},
            {"name": "str", "val": "7"},
        ]

        self.assertDictEqual(groupby(data, operator.itemgetter("name")), {
            "int": [{"name": "int", "val": 1}, {"name": "int", "val": 6}],
            "float": [{"name": "float", "val": 2.3}, {"name": "float", "val": 4.5}],
            "str": [{"name": "str", "val": "7"}],
        })


class TestMakeParts(TestCase):
    def test_usage(self):
        lst = list(range(10))
        part1, part2, part3, part4 = mkparts(lst, [1, 3, 6])
        self.assertListEqual(part1, [0])
        self.assertListEqual(part2, [1, 2])
        self.assertListEqual(part3, [3, 4, 5])
        self.assertListEqual(part4, [6, 7, 8, 9])

        head, middle, tail = mkparts(lst, [1, -1])
        self.assertEqual(head, [0])
        self.assertEqual(middle, [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(tail, [9])

    def test_special_val(self):
        empty_lst = []
        part1, part2, part3 = mkparts(empty_lst, [2, 4])
        self.assertListEqual(part1, [])
        self.assertListEqual(part2, [])
        self.assertListEqual(part3, [])

        lst = list(range(3))
        part1, part2 = mkparts(lst, [])
        self.assertListEqual(part1, [0])
        self.assertListEqual(part2, [1, 2])
        part1, part2 = mkparts(lst, [1])
        self.assertListEqual(part1, [0])
        self.assertListEqual(part2, [1, 2])

        part1, part2 = mkparts(lst, [4])
        self.assertListEqual(part1, [0, 1, 2])
        self.assertListEqual(part2, [])

        part1, part2, part3 = mkparts(lst, [1, 2])
        self.assertListEqual(part1, [0])
        self.assertListEqual(part2, [1])
        self.assertListEqual(part3, [2])

        part1, part2, part3 = mkparts(lst, [1, 1])
        self.assertListEqual(part1, [0])
        self.assertListEqual(part2, [])
        self.assertListEqual(part3, [1, 2])

        with self.assertRaisesRegexp(ValueError, "end index is less than start index"):
            part1, part2, part3 = mkparts(lst, [2, 1])

        with self.assertRaisesRegexp(ValueError, "end index is less than start index"):
            part1, part2, part3 = mkparts(lst, [2, -2])


class TestGetSingleItem(TestCase):
    def test_usage(self):
        mock_logger = mock.MagicMock()

        self.assertEqual(get_single_item([], logger=mock_logger), None)
        self.assertEqual(mock_logger.warning.call_count, 0)
        self.assertEqual(get_single_item([], 1, logger=mock_logger), 1)
        self.assertEqual(mock_logger.warning.call_count, 0)
        self.assertEqual(get_single_item([1], logger=mock_logger), 1)
        self.assertEqual(mock_logger.warning.call_count, 0)
        self.assertEqual(get_single_item([1, 2], logger=mock_logger), 1)
        self.assertEqual(mock_logger.warning.call_count, 1)


class TestDictMerge(TestCase):
    def test_usage(self):
        self.assertDictEqual(
            dict_merge([
                {1: 2, 2: 3},
                {2: 4, 3: 4},
                {4: 5},
            ]),
            {1: 2, 2: 3, 3: 4, 4: 5}
        )


class TestFlatten(TestCase):
    def test_usage(self):
        seq_list = [range(0, 3), range(3, 7), (i for i in range(7, 9))]
        self.assertListEqual(flatten(seq_list, list), range(0, 9))


class TestFindPeakItem(TestCase):
    def test_usage(self):
        self.assertListEqual(
            list(find_peak_item([13, 4, 5, 3, 6, 9, 4])),
            [(1, 4), (2, 5), (3, 3), (5, 9)]
        )
        self.assertListEqual(list(find_peak_item([13])), [])
        self.assertListEqual(list(find_peak_item([1, 2])), [])
        self.assertListEqual(list(find_peak_item([1, 2, 3])), [])
        self.assertListEqual(list(find_peak_item([1, 2, 1])), [(1, 2)])
        self.assertListEqual(list(find_peak_item([13], True)), [(0, 13)])
        self.assertListEqual(
            list(find_peak_item([1, 2], True)), [(0, 1), (1, 2)],
        )
        self.assertListEqual(
            list(find_peak_item([1, 2, 3], True)), [(0, 1), (2, 3)],
        )


class TestFilterN(TestCase):
    def test_filter_n(self):
        self.assertListEqual(
            [1, 3],
            list(filter_n(lambda x: x % 2, range(10), 2))
        )
        self.assertListEqual(
            [1],
            list(filter_n(None, range(10), 1))
        )
        self.assertListEqual(
            [0, 4, 8],
            list(filter_n(lambda x: x % 4 == 0, range(10), 20))
        )


class TestEveryN(TestCase):
    def test_every_n(self):
        self.assertListEqual(
            [(0, 1), (2, 3)],
            list(every_n(range(4), 2))
        )
        self.assertListEqual(
            [(0, 1, 2)],
            list(every_n(range(4), 3))
        )


class TestIterChunk(TestCase):
    def test_usage(self):
        seq = ""
        self.assertListEqual(list(iter_chunk(seq, 1)), [])
        self.assertListEqual(list(iter_chunk(seq, 2)), [])

        seq = "a"
        self.assertListEqual(list(iter_chunk(seq, 1)), ["a"])
        self.assertListEqual(list(iter_chunk(seq, 2)), ["a"])

        seq = "ab"
        self.assertListEqual(list(iter_chunk(seq, 1)), ["a", "b"])
        self.assertListEqual(list(iter_chunk(seq, 2)), ["ab"])

        seq = "abcde"
        self.assertListEqual(list(iter_chunk(seq, 1)), ["a", "b", "c", "d", "e"])
        self.assertListEqual(list(iter_chunk(seq, 2)), ["ab", "cd", "e"])
        self.assertListEqual(list(iter_chunk(seq, 3)), ["abc", "de"])


class TestSafeMax(TestCase):
    def test_usage(self):
        self.assertEqual(safe_max([3, 1, 5]), 5)
        self.assertIsNone(safe_max([]))
        self.assertEqual(safe_max([], 5), 5)


class TestSafeMin(TestCase):
    def test_usage(self):
        self.assertEqual(safe_min([3, 1, 5]), 1)
        self.assertIsNone(safe_min([]))
        self.assertEqual(safe_min([], 5), 5)
