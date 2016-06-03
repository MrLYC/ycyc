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

        obj = Object()
        self.assertIs(obj.first_visited_time, obj.first_visited_time)
        self.assertEqual(obj_mock.call_count, 2)


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


class TestCallImmediately(TestCase):
    def test_usage(self):
        num = 10
        init_val = 0

        @decoratorutils.call_immediately()
        def val_lst():
            return [init_val for i in range(num)]

        self.assertListEqual(val_lst, [
            init_val for i in range(num)
        ])


class TestMethodDecorator(TestCase):
    def test_usage(self):
        def add_one(func):
            return lambda: 1 + func()

        class AClass(object):
            def __init__(self, val):
                self.val = val

            @decoratorutils.method_decorator(add_one)
            def get_value(self):
                return self.val

        a = AClass(1)
        b = AClass(5)

        self.assertEqual(a.get_value(), 2)
        self.assertEqual(b.get_value(), 6)


class TestWithAttr(TestCase):
    def test_usage(self):
        @decoratorutils.withattr(alters_data=True, debug=True)
        def test_func(val):
            return val + 1

        self.assertTrue(test_func.alters_data)
        self.assertTrue(test_func.debug)
        self.assertEqual(test_func(0), 1)


class TestAllowUnboundMethod(TestCase):
    def test_usage(self):
        invokers = []

        class TestCls(object):
            @decoratorutils.allow_unbound_method
            def save_invoker(invoker):  # pylint: disable=E0213
                invokers.append(invoker)

        TestCls.save_invoker()  # pylint: disable=E1120
        self.assertEqual(TestCls, invokers.pop())

        test_obj = TestCls()
        test_obj.save_invoker()
        self.assertEqual(test_obj, invokers.pop())


class TestClassProperty(TestCase):
    def test_usage(self):
        class Model(object):
            @decoratorutils.classproperty
            def val(cls):  # pylint: disable=E0213
                return 1

        self.assertEqual(Model.val, 1)
        model = Model()
        self.assertEqual(model.val, 1)
