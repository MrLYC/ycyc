#!/usr/bin/env python
# encoding: utf-8

"""
A adapter tool module
"""

import collections
import sys
import functools
import types

from ycyc.base import funcutils


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


class DictAsObjAdapter(object):
    """
    Provided a adapter that allow visit a dict as object
    """

    def __init__(self, dct):
        self.__dict = dct

    def __getattr__(self, name):
        return self.__dict[name]

    def __setattr__(self, name, value):
        self.__dict[name] = value


class MappingMixin:

    def attrs_dict(self):
        return ObjAsDictAdapter(self)


def main_entry(main):
    """
    Call function `main` immediately if is in __main__ and exit
    """
    @functools.wraps(main)
    def wraped_main(*args, **kwg):
        result = main(*args, **kwg)
        return int(0 if result is None else result)

    if main.__module__ == "__main__":
        sys.exit(
            wraped_main()
            if main.func_code.co_argcount == 0
            else wraped_main(sys.argv)
        )

    return wraped_main


def proxy(obj):
    """
    A proxy to protect obj attributes will not be reassign
    """
    return type(
        "ProxyObject", (object,),
        {"__getattribute__": lambda _, k: getattr(obj, k)}
    )()


class DynamicClosure(object):

    def __init__(self, envs=()):
        from ycyc.base.iterutils import dict_merge

        self.environment = dict_merge(envs)

    def __call__(self, func, args, kwg):
        return func(self.environment.copy(), *args, **kwg)


def dynamic_closure(func, *args, **kwg):
    frame = funcutils.parent_frame()
    closure = DynamicClosure([frame.f_locals, frame.f_globals])
    return closure(func, args, kwg)


def attr_link(name):
    def getter(self):
        return getattr(self, name)

    def setter(self, value):
        return setattr(self, name, value)

    def deleter(self):
        return delattr(self, name)

    return property(getter, setter, deleter)
