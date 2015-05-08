#!/usr/bin/env python
# encoding: utf-8

"""
Debug helpers
"""

import functools
import pdb


def pdb_break(func):
    """
    set a debug break when function call
    :param func: function
    """
    @functools.wraps(func)
    def _(*args, **kwg):
        pdb.set_trace()
        return func(*args, **kwg)
    return _


def debug_call_trace(loger=None, name=None):
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
            loger.debug("%s[%d] call, args: %s, kwg: %s", fname, fid, args, kwg)
            try:
                res = func(*args, **kwg)
                loger.debug("%s[%s] return: %s", fname, fid, res)
                return res
            except Exception as err:
                loger.debug("%s[%d] got error: %s", fname, fid, err)
                raise
        return f
    return _
