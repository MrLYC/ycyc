#!/usr/bin/env python
# encoding: utf-8

import functools
import logging
import types

logger = logging.getLogger(__file__)


def call_trace(loger=None, name=None):
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
    def _(func):
        @functools.wraps(func)
        def f(*args, **kwg):
            with lock:
                return func(*args, **kwg)
        return f
    return _


class _CachedProperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        if not hasattr(self, "cached_result"):
            self.cached_result = types.MethodType(self.func, instance, cls)()
        return self.cached_result

    def __set__(self, obj, cls):
        raise AttributeError("can't set attribute")
cachedproperty = _CachedProperty
