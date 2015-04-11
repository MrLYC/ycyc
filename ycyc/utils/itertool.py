#!/usr/bin/env python
# encoding: utf-8


def getitems(obj, items, default=None):
    """
    Get items from obj
    :param obj: object
    :param items: string or iterable object
    :param default: default value
    :return: obj item value if existed, otherwise default value
    """
    if isinstance(items, (str, unicode)):
        items = (items,)

    try:
        return reduce(lambda x, i: x[i], items, obj)
    except IndexError, KeyError:
        return default


def getattrs(obj, attrs, default=None):
    """
    Get attrs from obj
    :param obj: object
    :param attrs: string or iterable object
    :param default: default value
    :return: obj attr value if existed, otherwise default value
    """
    if isinstance(attrs, (str, unicode)):
        attrs = (attrs,)

    try:
        return reduce(lambda x, n: getattr(x, n), attrs, obj)
    except AttributeError:
        return default
