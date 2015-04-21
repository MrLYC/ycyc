#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import mock

from ycyc.base.allowfail import AllowFail


class TestUsage(TestCase):
    @mock.patch("ycyc.base.allowfail.AllowFail.on_error")
    def test_decorator(self, magic_mock):
        @AllowFail("test func")
        def func():
            return 1

        result, exception = func()
        self.assertIsNone(exception)
        self.assertEqual(result, 1)
        self.assertIsNone(magic_mock.call_args)

    @mock.patch("ycyc.base.allowfail.AllowFail.on_error")
    def test_decorator_err(self, magic_mock):
        @AllowFail("test valueerror")
        def valueerror():
            raise ValueError("test exception")

        result, exception = valueerror()
        self.assertIsInstance(exception, ValueError)
        self.assertEqual(exception.message, "test exception")
        args = magic_mock.call_args[0]
        self.assertEqual(args[0], "test valueerror")
        self.assertIs(args[1], exception)

    @mock.patch("ycyc.base.allowfail.AllowFail.on_error")
    def test_contextmanager(self, magic_mock):
        with AllowFail("test contextmanager"):
            pass

        self.assertIsNone(magic_mock.call_args)

    @mock.patch("ycyc.base.allowfail.AllowFail.on_error")
    def test_contextmanager_err(self, magic_mock):
        with AllowFail("test contextmanager"):
            raise ValueError()

        args = magic_mock.call_args[0]
        self.assertEqual(args[0], "test contextmanager")
        self.assertTrue(isinstance(args[1], ValueError))
