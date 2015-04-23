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
