#!/usr/bin/env python
# encoding: utf-8

from ycyc.base import lazyutils

from unittest import TestCase


class TestLazyEnv(TestCase):
    def test_attr_usage(self):
        env = lazyutils.LazyEnv()
        env.a = lambda: global_a

        with self.assertRaisesRegexp(NameError, r"\bglobal_a\b"):
            env.a

        global_a = []
        self.assertIs(env.a, global_a)
        global_a = {}
        self.assertIsNot(env.a, global_a)

        env.a = global_a
        self.assertIs(env.a, global_a)

        global_a = ()
        env.a = lambda: global_a
        self.assertIs(env.a, global_a)

    def test_item_usage(self):
        import types

        env = lazyutils.LazyEnv()
        env["a"] = lambda: global_a

        self.assertIsInstance(env.a, types.LambdaType)
        self.assertIsInstance(env["a"], types.LambdaType)

        env.a = lambda: global_a
        with self.assertRaisesRegexp(NameError, r"\bglobal_a\b"):
            env.a

        global_a = []
        self.assertIs(env.a, global_a)
