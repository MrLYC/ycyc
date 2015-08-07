#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
import mock

from ycyc.frameworks.events import models


class TestEvent(TestCase):
    def test_usage(self):
        callback1 = mock.MagicMock()
        callback2 = mock.MagicMock()

        test_event = models.Event()
        test_event.notify("test1")

        test_event.register(callback1)
        test_event.notify("test2")
        callback1.assert_called_with("test2")

        test_event.register(callback2)
        test_event.notify("test3")
        callback1.assert_called_with("test3")
        callback2.assert_called_with("test3")

        callback1.side_effect = ValueError
        test_event.notify("test4")
        callback1.assert_called_with("test4")
        callback2.assert_called_with("test4")

        test_event.unregister(callback1)
        test_event.notify("test5")
        with self.assertRaises(AssertionError):
            callback1.assert_called_with("test5")
        callback2.assert_called_with("test5")

        test_event.unregister(callback2)
        test_event.notify("test6")
        with self.assertRaises(AssertionError):
            callback1.assert_called_with("test6")
        with self.assertRaises(AssertionError):
            callback2.assert_called_with("test6")