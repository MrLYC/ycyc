#!/usr/bin/env python
# encoding: utf-8

import functools
import pdb


def pdb_break(func):
    @functools.wraps(func)
    def _(*args, **kwg):
        pdb.set_trace()
        return func(*args, **kwg)
    return _
