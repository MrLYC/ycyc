#!/usr/bin/env python
# encoding: utf-8

import ast
import importlib
import inspect

DependencyModules = set()
ScriptPaths = None


class Analysis(ast.NodeTransformer):
    def __init__(self, paths):
        self.modules = set()
        self.paths = list(paths)

    def add_module(self, module):
        if module and module not in self.modules:
            self.modules.add(module)
            try:
                path = inspect.getsourcefile(importlib.import_module(module))
                if path:
                    self.paths.append(path)
            except:
                pass

    def visit_Import(self, node):
        for i in node.names:
            self.add_module(i.name)

    def visit_ImportFrom(self, node):
        self.add_module(node.module)

    def analysis(self):
        for p in self.paths:
            try:
                with open(p, "rt") as fp:
                    self.visit(ast.parse(fp.read(), p))
            except:
                pass
        return tuple(self.modules)

if __name__ == "__main__":
    import sys
    paths = sys.argv[1:]

    analysisor = Analysis(paths)
    for m in analysisor.analysis():
        print m
