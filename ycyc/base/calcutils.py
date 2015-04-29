#!/usr/bin/env python
# encoding: utf-8

import ast

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

    def __init__(self, locals):
        self.locals = locals

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in self.locals:
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
