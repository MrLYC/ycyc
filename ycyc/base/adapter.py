#!/usr/bin/env python
# encoding: utf-8

import collections
from functools import wraps


class ObjAsDictAdapter(collections.Mapping):
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


def withmanager(ctxmgr, *ctxargs, **ctxkwg):
    """call function with ctxmgr(*ctxargs, **ctxkwg)
    """
    def decorator(func):
        @wraps(func)
        def helper(*args, **kwg):
            with ctxmgr(*ctxargs, **ctxkwg):
                return func(*args, **kwg)

        return helper
    return decorator
