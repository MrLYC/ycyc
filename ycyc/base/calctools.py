#!/usr/bin/env python
# encoding: utf-8

import ast
from itertools import chain
from functools import partial

from ycyc.base import contextutils
from ycyc.base.iterutils import dict_merge, getitems

NameParseError = type("NameParseError", (NameError,), {})


class SafeCalc(ast.NodeTransformer):
    """
    Python expression safe calculator
    """
    globals = {
        "locals": None, "globals": None, "__name__": None,
        "__file__": None, "__builtins__": None, "True": True,
        "False": False,
    }

    def __init__(self, locals, allow_attr=True, timeout=0, interval=None):
        self.locals = locals
        if timeout:
            self.timeout = partial(contextutils.timeout, timeout, interval)
        else:
            self.timeout = contextutils.nothing
        self.allow_attr = allow_attr

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in self.locals and name not in self.globals:
                raise NameParseError("%s not found" % name)
        self.generic_visit(node)
        return node

    def visit_Attribute(self, node):
        name = node.attr
        if not self.allow_attr or name.startswith("__"):
            raise NameParseError("%s not allow" % name)
        self.generic_visit(node)
        return node

    def __call__(self, expr):
        ast_node = ast.parse(expr, mode="eval")
        ast_node = self.visit(ast_node)
        ast_node = ast.fix_missing_locations(ast_node)
        code = compile(ast_node, "<string>", mode="eval")
        with self.timeout():
            return eval(code, self.globals, self.locals)


def safecalc(expr, locals=None, **vars):
    """
    A quick function to calculate Python expression

    :param expr: Python expression
    :param locals: local env
    :param vars: variables
    :return: value
    """
    calc = SafeCalc(dict_merge((vars, locals or {})))
    return calc(expr)


def select(dct_object, *args, **kwg):
    """
    Select some items from complex dict object.
    """
    return {
        k: getitems(dct_object, i)
        for k, i in chain(enumerate(args), kwg.iteritems())
    }
