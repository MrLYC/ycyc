#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import mock

from ycyc.tools import rescuekit


class TestRescue(TestCase):
    def test_usage(self):
        self.assertIsInstance(
            rescuekit.Rescue.catch(""),  # pylint: disable=E1120
            rescuekit.Rescue
        )
        self.assertIsInstance(
            rescuekit.Rescue.meet(""),  # pylint: disable=E1120
            rescuekit.Rescue
        )

        func_mock = mock.MagicMock()
        rescue = rescuekit.Rescue.catch("")  # pylint: disable=E1120
        func_mock.return_value = 0
        self.assertEqual(rescue.call(func_mock, 1, val=2), 0)
        func_mock.assert_called_once_with(1, val=2)

        func_mock = mock.MagicMock()
        func_mock.side_effect = ValueError
        self.assertEqual(rescue.call(func_mock, val=3), "")
        func_mock.assert_called_once_with(val=3)

        rescue = rescuekit.Rescue.catch(
            "ValueError", ValueError
        ).catch(
            "KeyError", KeyError
        ).meet(
            "", None
        )
        func_mock = mock.MagicMock()
        func_mock.side_effect = ValueError
        self.assertEqual(rescue.call(func_mock), "ValueError")

        func_mock = mock.MagicMock()
        func_mock.side_effect = KeyError
        self.assertEqual(rescue.call(func_mock), "KeyError")

        func_mock = mock.MagicMock()
        func_mock.return_value = None
        self.assertEqual(rescue.call(func_mock), "")

        self.assertEqual(
            rescuekit.Rescue.catch("nan").call(lambda: 1 / 0),  # pylint: disable=E1120
            "nan"
        )
