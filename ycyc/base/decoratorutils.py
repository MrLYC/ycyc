#!/usr/bin/env python
# encoding: utf-8

"""
decoratorutils provided some useful decorators.
"""

import functools
import logging
import types

logger = logging.getLogger(__file__)


def call_trace(loger=None, name=None):
    """
    Trace a fun call with loger.
    :param loger: logging.Logger
    :param name: function name
    """
    def _(func):
        fname = name or func.func_name

        @functools.wraps(func)
        def f(*args, **kwg):
            fid = id(args) ^ id(kwg)
            loger.info("%s[%d] call", fname, fid)
            try:
                res = func(*args, **kwg)
                loger.info("%s[%s] return", fname, fid)
                return res
            except Exception as err:
                logger.info("%s[%d] got error: %s", fname, fid, err)
                raise
        return f
    return _


def with_lock(lock):
    """
    Call function with a lock
    :param lock: lock context manager
    """
    def _(func):
        @functools.wraps(func)
        def f(*args, **kwg):
            with lock:
                return func(*args, **kwg)
        return f
    return _


class CachedProperty(object):
    """
    Call func at first time and cached the result, return result
    immediately later.
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        if not hasattr(self, "cached_result"):
            result = types.MethodType(self.func, instance, cls)()
            setattr(instance, self.func.func_name, result)
        return result
cachedproperty = CachedProperty


def chainingmethod(func):
    """
    Declare a method is a chaining method which return self as returned value
    :param func: real func
    """
    @functools.wraps(func)
    def chaining(self, *args, **kwg):
        func(self, *args, **kwg)
        return self
    return chaining


def retry(num, errors=Exception):
    """
    Recall func when catched target errors at most num times
    :param num: maximum retry number, 0 for forever.
    :param errors: catch target errors
    """
    if num < 0:
        raise ValueError("num:%d can not less than 0" % num)

    def foo(func):
        @functools.wraps(func)
        def baz(*args, **kwg):
            i = num and num + 1
            while True:
                try:
                    return func(*args, **kwg)
                except errors:
                    i -= 1
                    if i == 0:
                        raise
        return baz
    return foo


def withmanager(ctxmgr, *ctxargs, **ctxkwg):
    """
    A decorator call function with ctxmgr, if ctxmgr is callable
    reset ctxmgr as ctxmgr(*ctxargs, **ctxkwg) every time.
    :param ctxmgr: context manager
    :param ctxargs: position argument
    :param ctxkwg: key word argument
    """
    def decorator(func):
        @functools.wraps(func)
        def helper(*args, **kwg):
            mgr = ctxmgr
            if callable(ctxmgr):
                mgr = ctxmgr(*ctxargs, **ctxkwg)
            with mgr:
                return func(*args, **kwg)

        return helper
    return decorator


def onerror_return(default_val, errors=Exception, callback=logger.warning):
    """
    return the default value when catch errors
    :param default_val: default value
    :param errors: catch exceptions(default: Exception)
    :param callback: callback when catched a exception(default: logger.warning)
    :return: func result if success else default_val
    """
    def foo(func):
        @functools.wraps(func)
        def baz(*args, **kwg):
            try:
                return func(*args, **kwg)
            except errors as err:
                if callback:
                    callback(err)
            return default_val
        return baz
    return foo
