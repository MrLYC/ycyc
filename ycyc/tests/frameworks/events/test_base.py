#!/usr/bin/env python
# encoding: utf-8

import mock

from unittest import TestCase

from ycyc.frameworks.events import base


class TestEvent(TestCase):
    def test_event(self):
        event = base.Event()

        mock_callback1 = event.register(mock.MagicMock(side_effect=ValueError))
        mock_callback2 = event.register(mock.MagicMock(return_value=0))

        with self.assertRaises(ValueError):
            event.notify(self)
        self.assertEqual(mock_callback1.call_count, 1)
        self.assertEqual(mock_callback2.call_count, 0)

        result = event.notify_all(self)
        self.assertEqual(mock_callback1.call_count, 2)
        self.assertEqual(mock_callback2.call_count, 1)

        self.assertIsNone(result[0].result)
        self.assertIsInstance(result[0].exception, ValueError)
        self.assertIs(result[0].callback, mock_callback1)

        self.assertEqual(result[1].result, 0)
        self.assertIsNone(result[1].exception)
        self.assertIs(result[1].callback, mock_callback2)

        event.unregister(mock_callback1)
        event.notify(self)
        self.assertEqual(mock_callback1.call_count, 2)
        self.assertEqual(mock_callback2.call_count, 2)

        with self.assertRaises(base.ListenerNoExistedError):
            event.unregister(mock_callback1)

        with self.assertRaises(base.ListenerDuplicatedError):
            event.register(mock_callback2)
