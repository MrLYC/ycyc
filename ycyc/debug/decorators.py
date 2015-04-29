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
