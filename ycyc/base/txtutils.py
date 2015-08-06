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


class TxtDistance(object):
    @classmethod
    def edit_distance(cls, s1, s2):
        """
        Simple algorithm to calculate the distance between two str

        :param s1: string 1
        :param s2: string 2
        :return: distance number
        """
        len1 = len(s1)
        len2 = len(s2)

        if (len1 <= 0) or (len2 <= 0):
            result = len1 or len2

        row_n = len1 + 1
        col_n = len2 + 1

        f_table = map(lambda x: [0] * col_n, range(row_n))
        for i in range(row_n):
            f_table[i][0] = i
        for i in range(col_n):
            f_table[0][i] = i

        for i in range(1, row_n):
            for j in range(1, col_n):
                if s1[i - 1] == s2[j - 1]:
                    f_table[i][j] = f_table[i - 1][j - 1]
                else:
                    f_table[i][j] = min([
                        f_table[i - 1][j] + 1,
                        f_table[i][j - 1] + 1,
                        f_table[i - 1][j - 1] + 1
                    ])
        return f_table[row_n - 1][col_n - 1]

    @classmethod
    def edit_distance2(cls, str1, str2):
        """
        Simple algorithm to calculate the distance between two str

        :param s1: string 1
        :param s2: string 2
        :return: distance number
        """
        called_result = {}

        def edit_distance(s1, s2):
            result = called_result.get((s1, s2))
            if result:
                return result

            len1 = len(s1)
            len2 = len(s2)
            ss1 = s1[1:]
            ss2 = s2[1:]
            if (len1 <= 0) or (len2 <= 0):
                result = len1 or len2
            elif s1[0] == s2[0]:
                result = edit_distance(ss1, ss2)
            else:
                result = 1 + min(
                    edit_distance(ss1, s2),
                    edit_distance(s1, ss2),
                    edit_distance(ss1, ss2),
                )
            called_result[(s1, s2)] = result
            return result

        return edit_distance(str1, str2)

    @classmethod
    def hamming_distance(cls, s1, s2):
        """
        Reutrn hamming distance between s1 and s2.
        This function assert that len(s1) == len(s2).

        :param s1: string 1
        :param s2: string 2
        :return: distance number
        """
        distance = 0
        for i, j in zip(s1, s2):
            if i != j:
                distance += 1
        return distance


def look_like(target, candidates):
    """
    choice one of string in candidates that target is looks like

    :param target: string
    :param candidates: string list
    :return: item in candidates
    """
    results = [
        (TxtDistance.edit_distance(target, i), i)
        for i in candidates
    ]
    result = min(*results, key=lambda x: x[0])
    return result[1]


def reversed_txt(txt):
    """
    Reverse a txt
    :param txt: string
    :return: reversed string
    """
    return txt[::-1]


def sep_join(sep, sequence, begin="", end=""):
    """
    Separator join each elements of sequence,
    if begin/end is True, insert the sep after
    or before the txt.you can also given some
    txt as head/tail of txt.

    :param sep: separator string
    :param sequence: string sequence
    :param begin: head of txt
    :param end: tail of txt
    :return: reversed string
    """
    txt = sep.join(sequence)
    if begin is True:
        txt = "%s%s" % (sep, txt)
    else:
        txt = "%s%s" % (begin, txt)

    if end is True:
        txt = "%s%s" % (txt, sep)
    else:
        txt = "%s%s" % (txt, end)
    return txt
