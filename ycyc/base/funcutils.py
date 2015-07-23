#!/usr/bin/env python
# encoding: utf-8

"""
funcutils provided some useful functions.
"""

import re
import operator
import inspect


def template_render(template, model):
    """
    A simple template render.
    Example:
    >>> model = {
    ...     "name": "lyc",
    ...     "foo": {
    ...       "bar": "hello"
    ...     }
    ...   }
    >>> template = "{{foo.bar}} {{ name }}"
    >>> template_render(template, model)

    :param template: template string
    :param model: dict model
    """
    parts = []
    for part in re.split(r"{{([\.\w]+?)}}", template):
        parts.append(str(
            part if len(parts) & 1 == 0 else
            reduce(lambda m, k: m[k], part.split("."), model)))
    return "".join(parts)


def encode(s, encoding="utf-8", errors="strict"):
    """
    Auto encode unicode string to bytes.
    :param s: string
    :param encoding: bytes encoding(default:utf-8)
    :param errors: different error handling scheme
    :return: bytes
    """
    if isinstance(s, bytes):
        return s

    return s.encode(encoding, errors)


def decode(s, encoding="utf-8", errors="strict"):
    """
    Auto decode bytes to unicode string.
    :param s: string
    :param encoding: bytes encoding(default:utf-8)
    :param errors: different error handling scheme
    :return: unicode
    """
    if isinstance(s, unicode):
        return s

    return s.decode(encoding, errors)


def bytescat(s1, s2, encoding="utf-8"):
    """
    Auto encode and return s1 + s2
    :param s1: string
    :param s2: string
    :param encoding: bytes encoding(default:utf-8)
    :return: bytes
    """
    return encode(s1, encoding) + encode(s2, encoding)


def strcat(s1, s2, encoding1="utf-8", encoding2=None):
    """
    Auto decode and return s1 + s2
    :param s1: string
    :param s2: string
    :param encoding1: bytes encoding of s1(default:utf-8)
    :param encoding2: bytes encoding of s2(default:same as encoding1)
    :return: bytes
    """
    encoding2 = encoding2 or encoding1
    return decode(s1, encoding1) + decode(s2, encoding2)


def drop_prefix(s, pattern):
    """
    Remove prefix pattern of a string.

    :param s: string
    :param pattern: string pattern
    """
    if s.startswith(pattern):
        return s[len(pattern):]
    return s


def drop_postfix(s, pattern):
    """
    Remove postfix pattern of a string.

    :param s: string
    :param pattern: string pattern
    """
    if s.endswith(pattern):
        return s[:-len(pattern)]
    return s


def split_and_strip(val_str, sep=","):
    """
    Simple split val_str by sep and drop strip the space chars for each items.

    :param val_str: string
    :param sep: split separator
    """
    return [
        i for i in (
            i.strip() for i in val_str.split(sep)
        )
        if i
    ]


def left_part_of(txt, sub_txt, n=1):
    """
    Return the left part before the nth of sub_txt appeared in txt.

    :param txt: text
    :param sub_txt: separate text
    :param n: the nth of sub_txt(default:1)
    """
    parts = txt.split(sub_txt)
    return sub_txt.join(parts[:n])


def right_part_of(txt, sub_txt, n=-1):
    """
    Return the right part after the nth of sub_txt appeared in txt.

    :param txt: text
    :param sub_txt: separate text
    :param n: the nth of sub_txt(default:-1)
    """
    parts = txt.split(sub_txt)
    return sub_txt.join(parts[n:])


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
