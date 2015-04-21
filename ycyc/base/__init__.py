#!/usr/bin/env python
# encoding: utf-8


def encode(s, encoding="utf-8", errors="strict"):
    if isinstance(s, bytes):
        return s

    return s.encode(encoding, errors)


def decode(s, encoding="utf-8", errors="strict"):
    if isinstance(s, unicode):
        return s

    return s.decode(encoding, errors)
