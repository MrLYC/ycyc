#!/usr/bin/env python
# encoding: utf-8

"""
A adapter tool module
"""

import collections
import sys


class ObjAsDictAdapter(collections.Mapping):
    """
    Provided a adapter that allow visit a object as dict
    """
    def __init__(self, obj):
        self.__object = obj

    def __getitem__(self, name):
        try:
            return getattr(self.__object, name)
        except AttributeError:
            raise KeyError(name)

    def __setitem__(self, name, value):
        setattr(self.__object, name, value)

    def __iter__(self):
        return iter(dir(self.__object))

    def __len__(self):
        return len(dir(self.__object))


def main_entry(main):
    """
    Call function `main` immediately if is in __main__ and exit
    """
    if main.__module__ != "__main__":
        return main

    result = main() if main.func_code.co_argcount == 0 else main(sys.argv)
    if result is None:
        result = 0
    else:
        result = int(result)

    sys.exit(result)
