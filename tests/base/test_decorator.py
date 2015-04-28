#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import mock

from ycyc.base import decorator


class TestCachedProperty(TestCase):
    def test_cachedproperty(self):
        from datetime import datetime

        obj_mock = mock.MagicMock(returnval=datetime.now())

        class Object(object):
            @decorator.cachedproperty
            def first_visited_time(self):
                return obj_mock()

        obj = Object()
        self.assertIs(obj.first_visited_time, obj.first_visited_time)
        self.assertEqual(obj_mock.call_count, 1)


class TestChainingMethod(TestCase):
    def test_chainingmethod(self):
        class MockCls(object):
            def __init__(self):
                self.called = []

            @decorator.chainingmethod
            def position_arg(self, val):
                self.called.append(("position_arg", val))

            @decorator.chainingmethod
            def keyword_arg(self, val):
                self.called.append(("keyword_arg", {"val": val}))

            @decorator.chainingmethod
            def free_args(self, *args, **kwg):
                self.called.append(("free_args", args, kwg))


        mockobj = MockCls()
        mockobj.position_arg(1).keyword_arg(val=2).free_args(3, val=4)

        self.assertEqual(mockobj.called.pop(), ("free_args", (3,), {"val": 4}))
        self.assertEqual(mockobj.called.pop(), ("keyword_arg", {"val": 2}))
        self.assertEqual(mockobj.called.pop(), ("position_arg", 1))


class TestRetry(TestCase):
    def mockfunc(self, iterator):
        try:
            n = next(iterator)
            raise ValueError("%s" % n)
        except StopIteration:
            return None

    def test_retry_useage(self):
        @decorator.retry(3)
        def mockfunc3(iterator):
            return self.mockfunc(iterator)

        @decorator.retry(0)
        def mockfunc0(iterator):
            return self.mockfunc(iterator)

        with self.assertRaisesRegexp(ValueError, "can not less than 0"):
            @decorator.retry(-1)
            def mockfunc(iterator):
                return self.mockfunc(iterator)

        self.assertIsNone(mockfunc3(iter(range(1))))
        self.assertIsNone(mockfunc3(iter(range(2))))
        self.assertIsNone(mockfunc3(iter(range(3))))
        with self.assertRaisesRegexp(Exception, "3"):
            mockfunc3(iter(range(4)))
        with self.assertRaisesRegexp(Exception, "3"):
            mockfunc3(iter(range(5)))

        self.assertIsNone(mockfunc0(iter(range(1))))
        self.assertIsNone(mockfunc0(iter(range(2))))
        self.assertIsNone(mockfunc0(iter(range(3))))
        self.assertIsNone(mockfunc0(iter(range(4))))
        self.assertIsNone(mockfunc0(iter(range(5))))
