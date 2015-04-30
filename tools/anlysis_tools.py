#!/usr/bin/env python
# encoding: utf-8

import ast
import logging

from ycyc.collections.tagmaps import TagMaps
from ycyc.libs.txtgen import TxtGenerator
from ycyc.base.iterutils import getfirst, mkparts

logger = logging.getLogger(__name__)


class Analysis(object):
    NodeAnalysisMaps = TagMaps()

    def __init__(self):
        self.analysis_result = TxtGenerator()

    def node_name(self, node):
        return node.__class__.__name__

    def analysis(self, path):
        with open(path, "rt") as fp:
            codes = fp.read()

        return self.analysis_ast(ast.parse(codes))

    def analysis_ast(self, module_ast):
        for node in module_ast.body:
            method = self.NodeAnalysisMaps.get(self.node_name(node))
            if method:
                method(self, node)
                self.analysis_result.writeline("")

        result = self.analysis_result.getval()
        self.analysis_result.clear()
        return result

    @NodeAnalysisMaps.register(NodeAnalysisMaps.DefaultKey)
    def visit_default(self, node):
        return False

    def var_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return "%s.%s" % (self.var_name(node.value), node.attr)
        raise TypeError("%s" % type(node))

    def get_docstring(self, node):
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            return ""
        ds_node = getfirst(node.body)
        if not isinstance(ds_node, ast.Expr):
            return ""
        ds_node = ds_node.value
        if not isinstance(ds_node, ast.Str):
            return ""
        return ds_node.s.lstrip("\n").rstrip()

    @NodeAnalysisMaps.register("Assign")
    def visit_assign(self, node):
        flag = False
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                continue
            flag = True
            self.analysis_result.writeline(
                "var: {name}",
                lineno=target.lineno,
                name=self.var_name(target),
            )
        return flag

    @NodeAnalysisMaps.register("FunctionDef")
    def visit_functiondef(self, node):
        node_args = node.args
        args_lst = [a.id for a in node_args.args]
        if node_args.vararg:
            args_lst.append("*%s" % node_args.vararg)
        if node_args.kwarg:
            args_lst.append("**%s" % node_args.kwarg)

        decorators = [
            "%s(*)" % d.attr if isinstance(d, ast.Call) else self.var_name(d)
            for d in node.decorator_list
        ]
        decorators.reverse()

        self.analysis_result.writeline(
            "function: {name}({args}){decorators}",
            lineno=node.lineno,
            name=node.name,
            args=", ".join(args_lst),
            decorators=(" @%s" % decorators) if decorators else "",
        )
        docstring = self.get_docstring(node)
        if docstring:
            self.analysis_result.writeline(
                "{docstring}\n--- docstring ---",
                docstring=docstring,
            )

    @NodeAnalysisMaps.register("ClassDef")
    def visit_classdef(self, node):
        basestr = ""
        if node.bases:
            basestr = "(%s)" % ", ".join([
                self.var_name(b) for b in node.bases
            ])

        self.analysis_result.writeline(
            "class: {name}{basestr}",
            name=node.name,
            basestr=basestr,
        )
        docstring = self.get_docstring(node)
        if docstring:
            self.analysis_result.writeline(
                "{docstring}\n--- docstring ---",
                docstring=docstring,
            )

        for node in node.body:
            method = self.NodeAnalysisMaps.get(self.node_name(node))
            if method:
                self.analysis_result.writeline("")
                self.analysis_result.write("+ ")
                method(self, node)

if __name__ == "__main__":
    import sys
    _, paths = mkparts(sys.argv, [1])

    analysisor = Analysis()
    for p in paths:
        print(p)
        print("===== result =====")
        print(analysisor.analysis(p))
