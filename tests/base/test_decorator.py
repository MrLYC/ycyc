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
