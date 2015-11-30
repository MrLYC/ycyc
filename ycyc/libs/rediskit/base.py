# encoding: utf-8

from itertools import chain


class RedisKit(object):
    @classmethod
    def factory(cls, *base_args, **base_kwargs):
        def constructor(*args, **kwargs):
            kwargs.update(base_kwargs)
            return cls(*chain(base_args, args), **kwargs)
        return constructor
