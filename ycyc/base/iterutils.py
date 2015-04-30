#!/usr/bin/env python
# encoding: utf-8

"""
iterutils provided some utils to operate a iterable or indexable object.
"""

import itertools
import collections


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
    except (IndexError, KeyError):
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


def iterable(obj):
    """
    Check obj if is iterable
    :param obj: object
    :return: boolean
    """
    return hasattr(obj, "__iter__")


def getnext(iterator, default=None):
    """
    Get next item of iterable object
    :param iterator: object
    :param default: default value
    :return: next item of iterator till the end, otherwise default value
    """
    try:
        return next(iterator)
    except StopIteration:
        return default


def getfirst(obj, default=None):
    """
    Get first item of iterable object
    :param obj: object
    :param default: default value
    :return: first item of obj if obj is not empty, otherwise default value
    """
    if not obj:
        return default
    return getnext(iter(obj), default)


def groupby(iterable, keyfunc):
    """
    Group iterable by keyfunc
    :param iterable: iterable obj
    :param keyfunc: group by keyfunc
    :return: dict {<keyfunc result>: [item1, item2]}
    """
    grouper = itertools.groupby(iterable, keyfunc)
    group_dict = collections.defaultdict(list)
    for k, r in grouper:
        group = group_dict[k]
        group.extend(r)
    return dict(group_dict)


def mkparts(sequence, indices=None):
    """
    Make some parts from sequence by indices
    :param sequence: indexable object
    :param indices: index list
    :return: [seq_part1, seq_part2, ...]
    """
    indices = indices or [1]
    result_list = collections.deque()
    start = 0
    seq_len = len(sequence)
    for end in indices:
        if end < 0:
            end = seq_len + end
        if end < start:
            raise ValueError("end index is less than start index")
        result_list.append(sequence[start:end])
        start = end
    result_list.append(sequence[start:])
    return result_list
