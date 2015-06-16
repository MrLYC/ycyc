#!/usr/bin/env python
# encoding: utf-8

import json
from functools import wraps

from ycyc.base.decoratorutils import cachedproperty


class RichTypeJSONEncoder(object):
    def __init__(self, type_mapping):
        self.__type_mapping = type_mapping

    @cachedproperty
    def encoder_factory(self):
        type_mapping = self.__type_mapping

        class JsonEncoder(json.JSONEncoder):
            def __init__(self, *args, **kwg):
                self.base = super(JsonEncoder, self)
                self.base.__init__(*args, **kwg)

            def default(self, data):  # pylint: disable=method-hidden
                factory = type_mapping.get(type(data))
                if factory:
                    return factory(data)
                try:
                    return self.base.default(data)
                except TypeError:
                    for typ, fcty in type_mapping.items():
                        if isinstance(data, typ):
                            return fcty(data)
                    raise
        return JsonEncoder

    @classmethod
    def default_type_mapping(cls):
        import datetime
        import decimal
        import collections
        import types

        return {
            set: list,
            frozenset: list,

            types.GeneratorType: list,
            types.XRangeType: list,

            collections.deque: list,
            collections.defaultdict: dict,
            collections.Counter: dict,
            collections.OrderedDict: dict,

            datetime.date: datetime.date.isoformat,
            datetime.datetime: datetime.datetime.isoformat,
            decimal.Decimal: float,

            (collections.Mapping, ): dict,
        }
