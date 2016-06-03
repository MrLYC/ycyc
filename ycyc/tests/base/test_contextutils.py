#!/usr/bin/env python
# encoding: utf-8

import time

from unittest import TestCase
import mock

from ycyc.base.contextutils import (
    catch, timeout, atlast, companion, heartbeat
)


class TestCatch(TestCase):
    def test_catch_errors(self):
        with catch():
            raise Exception()

        with catch(ZeroDivisionError):
            1 / 0

        with catch((KeyError, IndexError)):
            list()[1]
            dict()["nothing"]

    def test_raise(self):
        with self.assertRaises(KeyError):
            with catch(IndexError):
                dict()["nothing"]

        with self.assertRaises(IndexError):
            with catch(KeyError, reraise=IndexError):
                dict()["nothing"]

        with self.assertRaises(ValueError):
            with catch((ZeroDivisionError, IndexError), reraise=ValueError):
                1 / 0

        with self.assertRaises(ValueError):
            with catch((ZeroDivisionError, IndexError), reraise=ValueError):
                list()[1]

        with self.assertRaises(ValueError):
            try:
                valerr = ValueError()
                with catch(ZeroDivisionError, reraise=valerr):
                    1 / 0

            except ValueError as err:
                self.assertIs(err, valerr)
                raise

    def test_callback(self):
        results = []

        with catch((ZeroDivisionError, IndexError), callback=results.append):
            1 / 0
        self.assertIsInstance(results.pop(), ZeroDivisionError)

        with catch((ZeroDivisionError, IndexError), callback=results.append):
            list()[1]
        self.assertIsInstance(results.pop(), IndexError)

    def test_exec_info(self):
        with catch() as exec_info:
            self.assertTrue(exec_info["ok"])
            self.assertIsNone(exec_info["exception"])
            self.assertIsNone(exec_info["callback_returned"])

        self.assertTrue(exec_info["ok"])
        self.assertIsNone(exec_info["exception"])
        self.assertIsNone(exec_info["callback_returned"])

        callback = mock.MagicMock(return_value=1)
        with catch(NotImplementedError, callback=callback) as exec_info:
            raise NotImplementedError

        self.assertFalse(exec_info["ok"])
        self.assertIsInstance(exec_info["exception"], NotImplementedError)
        self.assertEqual(exec_info["callback_returned"], callback.return_value)


class TestCompanion(TestCase):
    def test_usage(self):
        mock_target = mock.MagicMock()
        with companion(mock_target) as thread:
            pass
        mock_target.assert_called_once_with()

        mock_target = mock.MagicMock()
        with companion(mock_target, auto_start=False) as thread:
            self.assertEqual(mock_target.call_count, 0)
            thread.start()
            time.sleep(0.001)
            self.assertEqual(mock_target.call_count, 1)


class TestTimeout(TestCase):
    def test_usage(self):
        import sys

        ticks = sys.getcheckinterval()

        with self.assertRaisesRegexp(RuntimeError, "timeout"):
            start = time.time()
            with timeout(0.01, 0.01):
                time.sleep(1)
        self.assertLess(time.time() - start, 1)
        self.assertEqual(ticks, sys.getcheckinterval())

        with self.assertRaises(KeyboardInterrupt):
            with timeout(0.01, 0.01):
                raise KeyboardInterrupt
        self.assertEqual(ticks, sys.getcheckinterval())

        with self.assertRaisesRegexp(RuntimeError, "timeout"):
            start = time.time()
            with timeout(0.01, 0.01, 10):
                while True:
                    pass
        self.assertLess(time.time() - start, 0.03)
        self.assertEqual(ticks, sys.getcheckinterval())

        # 0 for forever
        with timeout(0, 0.001):
            time.sleep(0.01)
        self.assertEqual(ticks, sys.getcheckinterval())


class TestAtlast(TestCase):
    def test_usage(self):
        func = mock.MagicMock()

        with atlast(func):
            self.assertEqual(func.call_count, 0)
        self.assertEqual(func.call_count, 1)

        with self.assertRaises(ZeroDivisionError):
            with atlast(func):
                1 / 0
        self.assertEqual(func.call_count, 1)

        with self.assertRaises(ZeroDivisionError):
            with atlast(func, force=True):
                1 / 0
        self.assertEqual(func.call_count, 2)


class TestHeartbeat(TestCase):
    def test_usage(self):
        mock_touch = mock.MagicMock()

        self.assertEqual(mock_touch.call_count, 0)
        with heartbeat(mock_touch, 0.01):
            call_count = mock_touch.call_count
            time.sleep(0.05)
            self.assertLess(call_count, mock_touch.call_count)
            call_count = mock_touch.call_count
            time.sleep(0.05)
            self.assertLess(call_count, mock_touch.call_count)

        call_count = mock_touch.call_count
        time.sleep(0.02)
        self.assertEqual(call_count, mock_touch.call_count)
