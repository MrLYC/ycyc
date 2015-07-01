#!/usr/bin/env python
# encoding: utf-8


def get_real_bases(bases):
    if bases is None:
        return (object,)
    if isinstance(bases, type):
        bases = (bases,)
    return tuple(bases)


def subtype(name, bases=None, attrs=None):
    return type(name, get_real_bases(bases), dict(attrs or {}))


class TypeFactory(object):
    def __getattr__(self, name):
        return lambda bases=None, attrs=None: subtype(
            name, bases, attrs,
        )

types_factory = TypeFactory()


def subexception(name, bases=None, attrs=None):
    return subtype(name, bases or [Exception], attrs)


class ExceptionFactory(object):
    def __getattr__(self, name):
        return lambda bases=None, attrs=None: subexception(
            name, bases, attrs,
        )

exceptions_factory = ExceptionFactory()
