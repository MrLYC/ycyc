#!/usr/bin/env python
# encoding: utf-8

"""
funcutils provided some useful functions.
"""

import inspect
import sys
import thread


def is_magic_method(method):
    """
    Check a method if is magic method

    :param method: method of a class
    """
    if not inspect.ismethod(method):
        return False
    func_name = method.im_func.func_name
    if func_name.startswith("__") and func_name.endswith("__"):
        return True
    return False


def set_default_attr(obj, name, value):
    """
    Set attribute to obj if attribute is not exists

    :param obj: object
    :param name: attribure name
    :param value: attribure value
    :return: if is attribute not exists
    """
    if not hasattr(obj, name):
        setattr(obj, name, value)
        return value
    return getattr(obj, name, value)


def iter_attrs(
    obj, include_fields=(), exclude_fields=(),
    public_only=True, exclude_methods=True,
):
    """
    iter attributes of obj

    :param obj: object
    :param include_fields: include all this fields if exists
    :param exclude_fields: exclude this fields
    :param public_only: choice public attr only
    :param exclude_methods: exclude methods
    """
    obj_type = type(obj)
    obj_type_name = obj_type.__name__
    for attr, val in inspect.getmembers(obj):
        if attr not in include_fields:
            if (
                attr in exclude_fields or
                attr.startswith("__") or
                attr.startswith("_%s__" % obj_type_name) or
                (public_only and attr.startswith("_")) or
                (exclude_methods and inspect.ismethod(val))
            ):
                continue
        yield attr, val


def parent_frame():
    """
    Return parent frame of invoker.
    """
    frames = sys._current_frames()
    current_frame = frames[thread.get_ident()]
    invoker_frame = current_frame.f_back
    return invoker_frame and invoker_frame.f_back


def export_module(name, env_locals=None):
    """
    Export module's attributes to invoker's locals, like:
        from xxx import *

    :param name: module name
    :param env_locals: invoker locals
    """
    import importlib

    if env_locals is None:
        frame = parent_frame()
        env_locals = frame.f_locals

    module = importlib.import_module(name)
    all_attrs = list(getattr(
        module, "__all__",
        (i for i in dir(module) if not i.startswith("_"))
    ))

    for i in all_attrs:
        env_locals[i] = getattr(module, i)

    return len(all_attrs)
