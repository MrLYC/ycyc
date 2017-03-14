#!/usr/bin/env python
# encoding: utf-8

from collections import namedtuple as _namedtuple
from itertools import chain
import logging

logger = logging.getLogger(__name__)


class NamedTuple(object):
    __Defaults__ = ()
    __Fields__ = ()
    __Requires__ = ()

    def __new__(cls, *args, **kwargs):
        params = dict(cls.__Defaults__)
        params.update(kwargs)
        i_args = iter(args)
        params.update({k: v for k, v in zip(cls.__Fields__, i_args)})
        return super(NamedTuple, cls).__new__(cls, *list(i_args), **params)


def namedtuple(name, requires=(), defaults=None):
    defaults = defaults or {}
    fields = tuple(i for i in chain(requires, defaults.keys()))
    return type(name, (NamedTuple, _namedtuple(name, fields)), {
        "__Defaults__": defaults,
        "__Fields__": fields,
        "__Requires__": requires,
    })
