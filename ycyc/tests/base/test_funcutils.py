#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.base import funcutils


class TestObjectHelper(TestCase):
    def test_is_magic_method(self):
        class Foo(object):
            def __str__(self):
                return "foo"

        foo = Foo()
        self.assertTrue(funcutils.is_magic_method(Foo.__str__))
        self.assertTrue(funcutils.is_magic_method(foo.__str__))

    def test_set_default_attr(self):
        class Foo(object):
            def __str__(self):
                return "foo"

        foo = Foo()
        self.assertFalse(hasattr(foo, "foobarbaz"))
        self.assertTrue(funcutils.set_default_attr(
            foo, "foobarbaz", True
        ))
        self.assertTrue(foo.foobarbaz)  # pylint: disable=E1101
        self.assertTrue(funcutils.set_default_attr(
            foo, "foobarbaz", False
        ))
        self.assertTrue(foo.foobarbaz)  # pylint: disable=E1101

    def test_iter_attrs(self):
        class Foo(object):
            Public = 0
            _Protected = 1
            __Privated = 2

            def __init__(self):
                self.public = 4
                self._protected = 5
                self.__privated = 6

            def get_privated(self):
                return self.__privated

            @property
            def protected(self):
                return self._protected

        foo = Foo()

        self.assertDictEqual(
            dict(funcutils.iter_attrs(foo)),
            {
                "Public": 0, "public": 4, "protected": 5,
            }
        )
        self.assertDictEqual(
            dict(funcutils.iter_attrs(foo, public_only=False)),
            {
                "Public": 0, "_Protected": 1, "public": 4,
                "protected": 5, "_protected": 5,
            }
        )
        self.assertDictEqual(
            dict(funcutils.iter_attrs(foo, include_fields={"_Protected"})),
            {
                "Public": 0, "_Protected": 1, "public": 4,
                "protected": 5,
            }
        )
        self.assertDictEqual(
            dict(funcutils.iter_attrs(foo, exclude_fields={"protected"})),
            {
                "Public": 0, "public": 4,
            }
        )
        result = dict(funcutils.iter_attrs(foo, exclude_methods=False))
        self.assertEqual(result["get_privated"], foo.get_privated)

        self.assertIn(
            "_Protected",
            dict(funcutils.iter_attrs(
                foo,
                include_fields={"_Protected"},
                exclude_fields={"_Protected"}
            ))
        )


class TestParentFrame(TestCase):
    def test_usage(self):
        import sys
        import thread

        frames = sys._current_frames()
        current_frame = frames[thread.get_ident()]
        frame = current_frame.f_back

        self.assertIs(frame, funcutils.parent_frame())


class TestExportModule(TestCase):
    def test_funcutils(self):
        locals_env = locals()
        export_module = funcutils.export_module(funcutils.__name__)
        for attr in dir(funcutils):
            if not attr.startswith("_"):
                self.assertIs(getattr(funcutils, attr), locals_env[attr])
            else:
                self.assertNotIn(attr, locals_env)

    def test_os(self):
        import os
        locals_env = locals()
        funcutils.export_module("os")
        for attr in os.__all__:
            self.assertIs(getattr(os, attr), locals_env[attr])
