#!/usr/bin/env python
# encoding: utf-8

import re


def template_render(template, model):
    parts = []
    for part in re.split(r"{{([\.\w]+?)}}", template):
        parts.append(str(
            part if len(parts) % 2 == 0 else
            reduce(lambda m, k: m[k], part.split("."), model)))
    return "".join(parts)


def encode(s, encoding="utf-8", errors="strict"):
    if isinstance(s, bytes):
        return s

    return s.encode(encoding, errors)


def decode(s, encoding="utf-8", errors="strict"):
    if isinstance(s, unicode):
        return s

    return s.decode(encoding, errors)


def bytescat(s1, s2, encoding="utf-8"):
    return encode(s1, encoding) + encode(s2, encoding)


def strcat(s1, s2, encoding1="utf-8", encoding2=None):
    encoding2 = encoding2 or encoding1
    return decode(s1, encoding1) + decode(s2, encoding2)
