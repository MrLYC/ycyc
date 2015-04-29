#!/usr/bin/env python
# encoding: utf-8

import types


class LazyEnv(object):
    """
    LazyEnv() is a environment manager which accept a lambda and
    get the result lazily.Use it as module global value manager
    to avoid recursive dependency of modules.
    Example:
        # module_a
        import module_b
        from lazyutils import LazyEnv
        GlobalEnv = LazyEnv()
        GlobalEnv.val = "a"
        GlobalEnv.txt = lambda: "i'm not " + module_b.GlobalEnv.val

        # module_b
        import module_a
        from lazyutils import LazyEnv
        GlobalEnv = LazyEnv()
        GlobalEnv.val = "b"
        GlobalEnv.txt = lambda: "i'm not " + module_a.GlobalEnv.val

    Anyway,it is not a suggested solution.
    You should use 'from xxx import xx' statement carefully.

    You can set a value immediately to LazyEnv(),there are two ways
    when you want to set a lambda:
        GlobalEnv.val = lambda: lambda: 1
        GlobalEnv["val"] = lambda: 1
    But LazyEnv() is not a dict like object.
    """
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
