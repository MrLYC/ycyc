#!/usr/bin/env python
# encoding: utf-8

import ast
import importlib
import inspect


class Analysis(ast.NodeTransformer):
    def __init__(self, paths, recursion):
        self.modules = list()
        self.paths = list(paths)
        self.recursion = recursion

    def add_module(self, module):
        if module and module not in self.modules:
            self.modules.append(module)
            if self.recursion:
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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("-r", "--recursion", action="store_true", default=False)
    args = parser.parse_args()

    analysisor = Analysis(args.paths, args.recursion)
    for m in analysisor.analysis():
        print m
