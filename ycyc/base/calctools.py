#!/usr/bin/env python
# encoding: utf-8

import ast
import inspect

from ycyc.base.contextutils import timeout

NameParseError = type("NameParseError", (NameError,), {})


def protect_f(obj):
    if inspect.isclass(obj):
        raise TypeError("%s" % type(obj))
    return obj


class SafeCalc(ast.NodeTransformer):
    """
    Python expression safe calculator
    """
    protect_fname = "_"
    globals = {
        "locals": None, "globals": None, "__name__": None,
        "__file__": None, "__builtins__": None, "True": True,
        "False": False, protect_fname: protect_f,
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
        node.value = self.make_protect(node.value)
        return node

    def make_protect(self, node):
        if isinstance(node, ast.Attribute):
            expr_node = ast.parse("%s()" % self.protect_fname, mode="eval")
            call_node = expr_node.body
            call_node.args.append(node)
            node = call_node
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
