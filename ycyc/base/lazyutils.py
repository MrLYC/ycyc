#!/usr/bin/env python
# encoding: utf-8

import types


class LazyEnv(object):
    def __setattr__(self, attr, val):
        if hasattr(self, attr):
            delattr(self, attr)
        super(LazyEnv, self).__setattr__("_lazy_%s" % attr, val)

    def __getattr__(self, attr):
        lazy_attr = "_lazy_%s" % attr
        if hasattr(self, lazy_attr):
            val = getattr(self, lazy_attr)
            if isinstance(val, types.LambdaType):
                val = val()
            super(LazyEnv, self).__setattr__(attr, val)
            delattr(self, lazy_attr)
            return val
        raise AttributeError("%s not found" % attr)

    def __setitem__(self, key, val):
        setattr(self, key, lambda: val)

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError("%s not found" % key)
