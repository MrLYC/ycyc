#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
import sys
import thread

from ycyc.base import logutils


class TestLoggerInfo(TestCase):
    def test_usage(self):
        frames = sys._current_frames()
        frame = frames[thread.get_ident()]
        loginfo = logutils.LoggerInfo()

        self.assertIs(frame, loginfo.frame)
        line_based = 18
        self.assertEqual(line_based + 1, loginfo.line_no)
        self.assertEqual(line_based + 2, loginfo.line_no)
        self_func = self.test_usage.im_func
        self.assertEqual(self_func.__name__, loginfo.code_name)
