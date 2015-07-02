#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

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
