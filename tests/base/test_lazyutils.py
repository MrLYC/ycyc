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


class TestLazyImport(TestCase):
    def test_usage(self):
        lazy_os = lazyutils.lazy_import("os")
        import os
        for attr in dir(os):
            self.assertIs(
                getattr(os, attr),
                getattr(lazy_os, attr),
            )

        lazy_lazyutils = lazyutils.lazy_import(lazyutils.__name__)
        for attr in dir(lazyutils):
            self.assertIs(
                getattr(lazyutils, attr),
                getattr(lazy_lazyutils, attr),
            )

        lazy_akulamatata = lazyutils.lazy_import("noting.akulamatata")
        with self.assertRaisesRegexp(
            ImportError, "No module named noting.akulamatata"
        ):
            lazy_akulamatata.fail()


def TestLazyKit(TestCase):
    def test_usage(self):
        gen = (i for i in range(3))
        lazy_list = lazyutils.LazyKit(lambda: list(gen))
        self.assertEqual(next(gen), 0)
        self.assertEqual(lazy_list[1], 1)
        self.assertEqual(lazy_list[2], 2)
        self.assertSetEqual(set(dir([])) - set(dir(lazy_list)), set())
