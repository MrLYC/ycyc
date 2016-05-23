#!/usr/bin/env python
# encoding: utf-8

"""
iterutils provided some utils to operate a iterable or indexable object.
"""

import itertools
import collections
import logging

logger = logging


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
    if not attrs:
        return obj

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
    data = sorted(iterable, key=keyfunc)
    return {
        k: list(g)
        for k, g in itertools.groupby(data, keyfunc)
    }


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
    return tuple(result_list)


def get_single_item(obj, default=None, logger=logger):
    """
    Get the single item from obj, if obj has more than 1 items, it
    will log a warning record.
    :param obj: iterable obj
    :param default: default value if obj is empty
    :return: obj first item
    """
    if obj and len(obj) > 1:
        logger.warning(
            "iterable object has more than 1 items, %s actually.", len(obj)
        )
    return getfirst(obj, default)


def dict_merge(dicts):
    """
    Merge dict list to a dict object
    :param dicts: dict list
    :return: dict
    """
    result = {}

    for d in dicts:
        for k, v in d.items():
            if k not in result:
                result[k] = v

    return result


def flatten(sequence_list, cls=list):
    """
    Flatten one level of nesting
    :param sequence_list: list of sequence
    :param cls: create instance of cls by flatten_gen
    :return: cls instance or generator
    """
    flatten_gen = itertools.chain.from_iterable(sequence_list)
    return cls(flatten_gen) if cls else flatten_gen


def find_peak_item(sequence, include_extremes=False):
    """
    Find peak item in sequence, yield each peak item with index.
    Example:
        >>> list(find_peak_item([13, 4, 5, 3, 6, 9, 4]))
        [(1, 4), (2, 5), (3, 3), (5, 9)]

    :param sequence: sequence
    :param include_extremes: include extreme points
    """
    iters = enumerate(sequence)
    index, left_p = next(iters)
    if include_extremes:
        yield index, left_p

    index, cur_p = next(iters)
    right_p = cur_p
    for r_idx, right_p in iters:
        if cmp(left_p, cur_p) * cmp(cur_p, right_p) < 0:
            yield index, cur_p
        left_p, cur_p, index = cur_p, right_p, r_idx

    if include_extremes:
        yield index, right_p


def filter_n(func_or_none, sequence, n=1):
    """
    Return n items in sequence which match func_or_none.

    :param func_or_none: judge function or None to choice items that are True
    :param sequence: iterable sequence
    :param n: choice n items at most
    """
    func = func_or_none or (lambda x: x)
    i_seq = iter(i for i in sequence if func(i))
    for i in range(n):
        yield next(i_seq)


def every_n(sequence, n=1):
    """
    Iterate every n items in sequence.

    :param sequence: iterable sequence
    :param n: n items to iterate
    """
    i_sequence = iter(sequence)
    return zip(*[i_sequence for i in range(n)])


def iter_chunk(sequence, size):
    """
    Iterate sequence as chunks

    :param sequence: iterable sequence
    :param size: size of every chunk
    """
    length = len(sequence)
    for i in range(0, length, size):
        yield sequence[i: i + size]


def safe_max(sequence, default=None):
    """
    Return the max value from sequence, if sequence is empty,
    return the default value.

    :param sequence: iterable sequence
    :param default: default value
    """
    i_seq = iter(sequence)
    try:
        value = next(i_seq)
    except StopIteration:
        return default

    return max(itertools.chain(sequence, [value]))


def safe_min(sequence, default=None):
    """
    Return the min value from sequence, if sequence is empty,
    return the default value.

    :param sequence: iterable sequence
    :param default: default value
    """
    i_seq = iter(sequence)
    try:
        value = next(i_seq)
    except StopIteration:
        return default

    return min(itertools.chain(sequence, [value]))
