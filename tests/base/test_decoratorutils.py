#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import mock

from ycyc.base import decoratorutils


class TestCachedProperty(TestCase):
    def test_cachedproperty(self):
        from datetime import datetime

        obj_mock = mock.MagicMock(returnval=datetime.now())

        class Object(object):
            @decoratorutils.cachedproperty
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

            @decoratorutils.chainingmethod
            def position_arg(self, val):
                self.called.append(("position_arg", val))

            @decoratorutils.chainingmethod
            def keyword_arg(self, val):
                self.called.append(("keyword_arg", {"val": val}))

            @decoratorutils.chainingmethod
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
        @decoratorutils.retry(3)
        def mockfunc3(iterator):
            return self.mockfunc(iterator)

        @decoratorutils.retry(0)
        def mockfunc0(iterator):
            return self.mockfunc(iterator)

        with self.assertRaisesRegexp(ValueError, "can not less than 0"):
            @decoratorutils.retry(-1)
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


class TestWithManager(TestCase):
    def test_withmanager(self):
        ctxmgr_cls = mock.MagicMock()
        ctxmgr_obj = mock.MagicMock()
        ctxmgr_cls.return_value = ctxmgr_obj
        enter_mock = mock.MagicMock()
        exit_mock = mock.MagicMock()
        setattr(ctxmgr_obj, "__enter__", enter_mock)
        setattr(ctxmgr_obj, "__exit__", exit_mock)

        @decoratorutils.withmanager(ctxmgr_cls, 1, 2, k=3)
        def func1(k):
            return k + 1

        @decoratorutils.withmanager(lambda: ctxmgr_obj)
        def func2(k):
            return k + 1
        self.assertEqual(func1(4), 5)
        self.assertEqual(ctxmgr_cls.call_count, 1)
        self.assertEqual(ctxmgr_cls.call_args[0], (1, 2))
        self.assertEqual(ctxmgr_cls.call_args[1], {"k": 3})
        self.assertEqual(ctxmgr_obj.call_count, 0)
        self.assertEqual(enter_mock.call_count, 1)
        self.assertEqual(exit_mock.call_count, 1)

        self.assertEqual(func2(5), 6)
        self.assertEqual(ctxmgr_cls.call_count, 1)
        self.assertEqual(ctxmgr_obj.call_count, 0)
        self.assertEqual(enter_mock.call_count, 2)
        self.assertEqual(exit_mock.call_count, 2)


class TestOnErrorReturn(TestCase):
    def test_usage(self):
        callback_mock = mock.MagicMock()

        @decoratorutils.onerror_return(None, StopIteration, callback_mock)
        def gen_next(gen):
            return next(gen)

        gen = (i for i in range(2))
        self.assertEqual(gen_next(gen), 0)
        self.assertEqual(gen_next(gen), 1)
        self.assertEqual(callback_mock.call_count, 0)
        self.assertEqual(gen_next(gen), None)
        self.assertEqual(callback_mock.call_count, 1)

        gen = (i / 0 for i in range(2))
        with self.assertRaises(ZeroDivisionError):
            gen_next(gen)

        self.assertEqual(callback_mock.call_count, 1)
