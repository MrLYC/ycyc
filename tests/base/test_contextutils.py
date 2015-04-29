#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.base.contextutils import catch


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
