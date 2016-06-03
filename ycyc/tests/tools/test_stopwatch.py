#!/usr/bin/env python
# encoding: utf-8

import time

from unittest import TestCase

from ycyc.tools import stopwatch


class TestStopwatch(TestCase):
    def test_usage(self):
        s_watch = stopwatch.Stopwatch()

        self.assertAlmostEqual(s_watch.duration, 0)
        self.assertIsNone(s_watch.start_on)

        s_watch.enable = True
        start_on1 = time.time()
        self.assertIsNotNone(s_watch.start_on)
        self.assertTrue(s_watch.enable)
        self.assertGreater(s_watch.duration, 0)

        start_on2 = s_watch.start_on
        duration1 = s_watch.duration
        s_watch.enable = False
        duration2 = s_watch.duration
        self.assertEqual(s_watch.start_on, start_on2)
        self.assertFalse(s_watch.enable)
        self.assertEqual(s_watch.duration, duration2)

        duration3 = time.time() - start_on1
        s_watch.enable = True
        self.assertLess(s_watch.duration, duration3)
        self.assertGreater(s_watch.duration, duration1)
        self.assertGreater(s_watch.start_on, start_on2)
