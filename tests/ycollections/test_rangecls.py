#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
from datetime import datetime, timedelta

from ycyc.ycollections import rangecls


class TestARange(TestCase):
    def test_constructor(self):
        r = rangecls.ARange(0, 2)
        self.assertTrue(r.include_start)
        self.assertTrue(r.include_end)

        with self.assertRaises(rangecls.RangeError):
            rangecls.ARange(5, 2)

    def test_contains(self):
        r = rangecls.ARange(0, 2)
        self.assertTrue(0 in r)
        self.assertTrue(1 in r)
        self.assertTrue(2 in r)

        r = rangecls.ARange(0, 2, include_start=False, include_end=False)
        self.assertFalse(0 in r)
        self.assertTrue(1 in r)
        self.assertFalse(2 in r)

    def test_overlapping(self):
        r1 = rangecls.ARange(0, 5)
        r2 = rangecls.ARange(1, 3)

        r3 = r1 & r2
        self.assertEqual(r3.start, 1)
        self.assertEqual(r3.end, 3)
        self.assertEqual(r3.include_start, True)
        self.assertEqual(r3.include_end, True)

        r4 = r2 & r1
        self.assertEqual(r4.start, 1)
        self.assertEqual(r4.end, 3)
        self.assertEqual(r4.include_start, True)
        self.assertEqual(r4.include_end, True)

        r1 = rangecls.ARange(0, 2)
        r2 = rangecls.ARange(1, 3)

        r3 = r1 & r2
        self.assertEqual(r3.start, 1)
        self.assertEqual(r3.end, 2)
        self.assertEqual(r3.include_start, True)
        self.assertEqual(r3.include_end, True)

        r4 = r2 & r1
        self.assertEqual(r4.start, 1)
        self.assertEqual(r4.end, 2)
        self.assertEqual(r4.include_start, True)
        self.assertEqual(r4.include_end, True)

        r1 = rangecls.ARange(1, 2)
        r2 = rangecls.ARange(4, 5)
        self.assertEqual(r1 & r2, None)
        self.assertEqual(r2 & r1, None)

    def test_point_position(self):
        r = rangecls.ARange(1, 3)
        self.assertTrue(r.is_after_of(0))
        self.assertTrue(r.is_before_of(4))
        self.assertFalse(r.is_after_of(2))
        self.assertFalse(r.is_before_of(2))
        self.assertFalse(r.is_after_of(4))
        self.assertFalse(r.is_before_of(0))

        r = rangecls.ARange(0, 2, include_start=False, include_end=False)
        self.assertFalse(r.is_after_of(2))
        self.assertTrue(r.is_before_of(2))
        self.assertTrue(r.is_after_of(0))
        self.assertFalse(r.is_before_of(0))

    def test_sub_range(self):
        r1 = rangecls.ARange(0, 5)
        r2 = rangecls.ARange(1, 3)
        self.assertTrue(r1.has_sub_range(r2))
        self.assertTrue(r1.has_sub_range(r1))
        self.assertFalse(r2.has_sub_range(r1))
        self.assertTrue(r2.has_sub_range(r2))

        r3 = rangecls.ARange(0, 2, include_start=False, include_end=False)
        r4 = rangecls.ARange(0, 2)
        r5 = rangecls.ARange(0, 3, include_start=False)
        self.assertTrue(r4.has_sub_range(r3))
        self.assertTrue(r5.has_sub_range(r3))
        self.assertFalse(r5.has_sub_range(r4))

    def test_is_follow_by(self):
        r1 = rangecls.ARange(0, 3)
        r2 = rangecls.ARange(0, 3, include_end=False)
        r3 = rangecls.ARange(3, 6)
        r4 = rangecls.ARange(3, 6, include_start=False)
        r5 = rangecls.ARange(4, 6)

        self.assertFalse(r1.is_follow_by(r3))
        self.assertTrue(r1.is_follow_by(r4))
        self.assertFalse(r1.is_follow_by(r5))

        self.assertTrue(r2.is_follow_by(r3))
        self.assertFalse(r2.is_follow_by(r4))
        self.assertFalse(r2.is_follow_by(r5))

    def test_sampling(self):
        r = rangecls.ARange(0, 4)
        self.assertListEqual(list(r.sampling(1)), [0, 1, 2, 3, 4])
        self.assertListEqual(list(r.sampling(2)), [0, 2, 4])

        r = rangecls.ARange(0, 4, include_start=False)
        self.assertListEqual(list(r.sampling(2)), [2, 4])

        r = rangecls.ARange(0, 4, include_start=False, include_end=False)
        self.assertListEqual(list(r.sampling(2)), [2])
        self.assertListEqual(list(r.sampling(1.25)), [1.25, 2.5, 3.75])

        r = rangecls.ARange(datetime(2010, 12, 18), datetime(2015, 4, 26))
        self.assertEqual(len(list(r.sampling(timedelta(days=1)))), 1591)
