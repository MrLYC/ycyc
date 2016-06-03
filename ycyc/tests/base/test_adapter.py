#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
import inspect

import mock

from ycyc.tests import mock_patches
from ycyc.base import adapter


class TestObjAsDictAdapter(TestCase):

    class Parent(object):
        pclsval = 1

        def __init__(self):
            self.pinsval = 2

    class Child(Parent):
        cclsval = 3

        def __init__(self):
            super(TestObjAsDictAdapter.Child, self).__init__()
            self.cinsval = 4

        def __getattr__(self, name):
            if name == "dynamicval":
                return 5

    def test_base_method(self):
        parent = self.Parent()
        parent_dict = adapter.ObjAsDictAdapter(parent)

        self.assertEqual(parent_dict["pclsval"], parent.pclsval)
        self.assertEqual(parent_dict["pinsval"], parent.pinsval)
        self.assertIn("pclsval", iter(parent_dict))
        self.assertIn("pinsval", iter(parent_dict))

    def test_inherit(self):
        child = self.Child()
        child_dict = adapter.ObjAsDictAdapter(child)

        self.assertEqual(child_dict["pclsval"], child.pclsval)
        self.assertEqual(child_dict["pinsval"], child.pinsval)
        self.assertEqual(child_dict["cclsval"], child.cclsval)
        self.assertEqual(child_dict["cinsval"], child.cinsval)
        self.assertIn("pclsval", iter(child_dict))
        self.assertIn("pinsval", iter(child_dict))
        self.assertIn("cclsval", iter(child_dict))
        self.assertIn("cinsval", iter(child_dict))

    def test_dynamic_attr(self):
        child = self.Child()
        child_dict = adapter.ObjAsDictAdapter(child)

        self.assertEqual(child_dict["dynamicval"], child.dynamicval)
        self.assertNotIn("dynamicval", iter(child_dict))

        child.dynamicval = 6
        self.assertEqual(child_dict["dynamicval"], child.dynamicval)
        self.assertIn("dynamicval", iter(child_dict))

    def test_dict_interface(self):
        child = self.Child()
        parent = self.Parent()
        child_dict = adapter.ObjAsDictAdapter(child)
        parent_dict = adapter.ObjAsDictAdapter(parent)

        self.assertEqual(parent_dict.get("cinsval"), None)
        self.assertEqual(
            parent_dict.get("cinsval", child_dict["cinsval"]),
            child_dict.get("cinsval"))

        self.assertGreater(len(parent_dict), 0)
        self.assertEqual(parent_dict.keys(), list(parent_dict.iterkeys()))
        self.assertEqual(parent_dict.values(), list(parent_dict.itervalues()))
        self.assertEqual(parent_dict.items(), list(parent_dict.iteritems()))
        self.assertEqual(len(parent_dict), len(list(parent_dict)))


class TestMainEntry(TestCase):

    @property
    def main_mock(self):
        main_mock = mock.MagicMock()
        main_mock.func_name = main_mock.__name__ = "main_mock"
        main_mock.func_doc = main_mock.__doc__ = "main_mock doc"
        main_mock.func_globals = mock.MagicMock()
        main_mock.func_defaults = mock.MagicMock()
        main_mock.func_code = mock.MagicMock()
        return main_mock

    def test_usage(self):
        with mock_patches(
            "ycyc.base.adapter.sys",
        ) as patches:
            main_mock = self.main_mock
            main_mock.return_value = 1

            new_main = adapter.main_entry(main_mock)
            self.assertEqual(new_main(1, 2, 3), main_mock.return_value)
            main_mock.assert_called_once_with(1, 2, 3)

        with mock_patches(
            "ycyc.base.adapter.sys",
        ) as patches:
            main_mock = self.main_mock
            main_mock.__module__ = "__main__"
            main_mock.func_code.co_argcount = 0
            main_mock.return_value = 1

            new_main = adapter.main_entry(main_mock)

            main_mock.assert_called_once_with()
            patches.sys.exit.assert_called_once_with(main_mock.return_value)

        with mock_patches(
            "ycyc.base.adapter.sys",
        ) as patches:
            patches.sys.argv = [id(patches)]
            main_mock = self.main_mock
            main_mock.__module__ = "__main__"
            main_mock.func_code.co_argcount = 1
            main_mock.return_value = None

            new_main = adapter.main_entry(main_mock)

            main_mock.assert_called_once_with(patches.sys.argv)
            patches.sys.exit.assert_called_once_with(0)


class TestProxy(TestCase):

    def test_usage(self):
        mock_object = mock.MagicMock()
        mock_object.value = "lyc"
        proxy_object = adapter.proxy(mock_object)

        self.assertEqual(mock_object.value, proxy_object.value)  # pylint: disable=E1101

        value = proxy_object.value = 123
        self.assertNotEqual(mock_object.value, value)
        self.assertEqual(mock_object.value, proxy_object.value)  # pylint: disable=E1101

        value = mock_object.value = 123
        self.assertEqual(mock_object.value, value)
        self.assertEqual(mock_object.value, proxy_object.value)  # pylint: disable=E1101

        @adapter.proxy
        class Consts(object):
            A = 1
            B = 2

        Consts.A = 2
        self.assertEqual(Consts.A, 1)

        Consts.B = 3
        self.assertEqual(Consts.B, 2)


class TestDynamicClosure(TestCase):

    def test_usage(self):
        def check(env):
            self.assertEqual(env["l_value"], g_value)

        def invoker(value):
            l_value = value
            adapter.dynamic_closure(check)

        g_value = 1
        invoker(g_value)
        g_value = 2
        invoker(g_value)


class TestAttrLink(TestCase):

    def test_usage(self):
        class A(object):
            a = 1
            b = adapter.attr_link("a")

        a = A()
        self.assertIs(a.a, a.b)
        a.a = 2
        self.assertIs(a.b, 2)
        a.b = 3
        self.assertIs(a.a, 3)
