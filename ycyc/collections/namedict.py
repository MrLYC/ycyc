#!/usr/bin/env python
# encoding: utf-8

import six
from collections import OrderedDict
from itertools import chain
import logging

from ycyc.base.contextutils import catch

logger = logging.getLogger(__name__)


class RequireFieldsMissError(Exception):
    pass


class NamedDictMeta(type):
    def __new__(cls, name, base, attrs):
        fields = attrs.pop("__Fields__", {})
        attrs["__Fields__"] = OrderedDict(fields)

        requires = attrs.pop("__Requires__", ())
        attrs["__Requires__"] = tuple(requires)

        return type.__new__(cls, name, base, attrs)


class NamedDict(six.with_metaclass(NamedDictMeta, dict)):
    def __init__(self, *args, **kwg):  # pylint: disable=E1002
        requires = self.__Requires__
        fields = self.__Fields__.copy()
        field_keys = fields.viewkeys()
        real_keys = field_keys | set(requires)

        if kwg:
            kwg_keys = kwg.viewkeys()
            undefined_keys = kwg_keys - real_keys
            if undefined_keys:
                logger.warning("undefined keys: %s", undefined_keys)

            fields.update({
                k: kwg[k]
                for k in real_keys & kwg_keys
            })
        if args:
            i_args = iter(args)
            fields.update({
                k: v
                for k, v in zip(chain(requires, field_keys), i_args)
            })

            remain_args = list(i_args)
            if remain_args:
                logger.warning("not acceptable arguments: %s", remain_args)

        missed_fields = set(requires) - set(fields.keys())
        if missed_fields:
            logger.debug("missed_fields: %s", missed_fields)
            raise RequireFieldsMissError(
                "fields: [%s]" % ", ".join(missed_fields)
            )

        super(NamedDict, self).__init__(fields)

    def __getattr__(self, name):
        with catch(KeyError, reraise=AttributeError):
            return self[name]

    def __setattr__(self, name, key):
        self[name] = key


def namedict(name, requires=(), fields=None):
    """
    Return a subclass of dict with named fields

    :param fields: option fields
    :param requires: requires fields
    """
    return type(name, (NamedDict,), {
        "__Fields__": fields or {},
        "__Requires__": requires,
    })
