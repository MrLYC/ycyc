#!/usr/bin/env python
# encoding: utf-8

"""
funcutils provided some useful functions.
"""

import inspect


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
                attr in exclude_fields
                or attr.startswith("__")
                or attr.startswith("_%s__" % obj_type_name)
                or (public_only and attr.startswith("_"))
                or (exclude_methods and inspect.ismethod(val))
            ):
                continue
        yield attr, val


def filter_n(func_or_none, sequence, n=1):
    """
    Return n items in sequence which match func_or_none.

    :param func_or_none: judge function or None to choice items that are True
    :param sequence: iterable sequence
    :param n: choice n items at most
    """
    func = func_or_none or (lambda x: x)
    result = []
    cnt = 0
    for i in sequence:
        if cnt >= n:
            break
        if func(i):
            result.append(i)
            cnt += 1
    return result
