#!/usr/bin/env python
# encoding: utf-8

import types
import functools
import importlib
import sys

try:
    from importlib import reload
except ImportError:
    pass


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

    def __init__(self, **attrs):
        super(LazyEnv, self).__setattr__("_env", attrs)

    def __setattr__(self, attr, val):
        self[attr] = val

    def __getattr__(self, attr):
        if attr in self._env:
            val = self._env[attr]
            if isinstance(val, types.LambdaType):
                val = val()
            self._env.pop(attr)
            super(LazyEnv, self).__setattr__(attr, val)
            return val
        raise AttributeError("%s not found" % attr)

    def __setitem__(self, key, val):
        if hasattr(self, key):
            delattr(self, key)
        self._env[key] = val

    def __getitem__(self, key):
        return self._env[key]


def lazy_init(func):
    """
    Decorator for __getattr__ method only, cached the real __getattr__
    method returned value and init the attribute.
    """
    assert func.__name__ == "__getattr__"

    @functools.wraps(func)
    def lazy_get(self, name):
        value = func(self, name)
        setattr(self, name, value)
        return value

    return lazy_get


class FakeModule(object):
    @classmethod
    def reload(cls, module):
        """
        Reload the fake module
        """
        real_module = sys.modules[module.__name__]
        reload(real_module)
        return module

    def __getattr__(self, name):
        raise NotImplementedError


def lazy_import(module_name):
    """
    Lazy to import a module
    """
    def getattribute(self, attr):
        module = importlib.import_module(module_name)
        self.__dict__ = module.__dict__
        return getattr(module, attr)

    return type(
        FakeModule.__name__,
        (FakeModule,),
        {"__getattribute__": getattribute}
    )()


class LazyKit(object):
    def __init__(self, factory):
        self.__factory = factory

    def __getattr__(self, name):
        if not hasattr(self, "__object"):
            self.__object = self.__factory()
        return getattr(self.__object, name)
