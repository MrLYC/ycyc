#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
import mock

from ycyc.base.contextutils import (
    catch, timeout, atlast
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


class TestTimeout(TestCase):
    def test_usage(self):
        import time

        with self.assertRaisesRegexp(RuntimeError, "timeout"):
            start = time.time()
            with timeout(0.01, 0.01):
                time.sleep(1)
        self.assertLess(time.time() - start, 1)

        with self.assertRaises(KeyboardInterrupt):
            with timeout(0.01, 0.01):
                raise KeyboardInterrupt

        # 0 for forever
        with timeout(0, 0.001):
            time.sleep(0.01)


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
