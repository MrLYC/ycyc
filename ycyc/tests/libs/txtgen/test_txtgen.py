#!/usr/bin/env python
# encoding: utf-8

from collections import OrderedDict
from unittest import TestCase
import textwrap

from ycyc.libs import txtgen


class Test_TxtGenerator(TestCase):
    def test_usage(self):
        gen = txtgen.TxtGenerator({
            "clsname": "NewClass", "basecls": "object",
            "attrname": "new_attr", "initval": "None"
        })
        cls_meta = (
            {
                "clsname": "TestUsage",
                "basecls": "TestCase",
                "attrs": OrderedDict([
                    ("a", "1"),
                    ("b", "None"),
                ]),
            },
            {
                "clsname": "Model",
                "basecls": "BaseModel",
                "attrs": OrderedDict([
                    ("age", "0"),
                    ("name", "''"),
                ]),
            },
            {
                "clsname": "Tool",
                "attrs": {
                    "name": "'tools'",
                },
            },
        )

        for i in cls_meta:
            gen.writeline("class {clsname}({basecls}):", **i)
            for name, val in i["attrs"].iteritems():
                gen.writeline("    {attrname} = {initval}", attrname=name, initval=val)
            gen.writeline("")

        self.assertEqual(gen.getval().strip(), textwrap.dedent("""
            class TestUsage(TestCase):
                a = 1
                b = None

            class Model(BaseModel):
                age = 0
                name = ''

            class Tool(object):
                name = 'tools'""").strip())
