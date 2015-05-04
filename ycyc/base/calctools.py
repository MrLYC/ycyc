#!/usr/bin/env python
# encoding: utf-8

import ast

from ycyc.base.contextutils import timeout

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

    def __init__(self, locals, timeout=0, interval=None):
        self.locals = locals
        self.timeout = timeout
        self.interval = interval

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in self.locals and name not in self.globals:
                raise NameParseError("%s not found" % name)
        self.generic_visit(node)
        return node

    def visit_Attribute(self, node):
        name = node.attr
        if name.startswith("__"):
            raise NameParseError("%s not allow" % name)
        self.generic_visit(node)
        return node

    def __call__(self, expr):
        ast_node = ast.parse(expr, mode="eval")
        ast_node = self.visit(ast_node)
        ast_node = ast.fix_missing_locations(ast_node)
        code = compile(ast_node, "<string>", mode="eval")
        with timeout(self.timeout, self.interval):
            return eval(code, self.globals, self.locals)


def safecalc(expr, **locals):
    """
    A quick function to calculate Python expression
    :param expr: Python expression
    :param locals: variables
    :return: value
    """
    calc = SafeCalc(locals)
    return calc(expr)
