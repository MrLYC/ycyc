#!/usr/bin/env python
# encoding: utf-8


class Marker(object):
    __slots__ = ["name", "value"]

    def __init__(self, name=NotImplemented, value=NotImplemented):
        self.name = (
            "Mark[%s]" % id(self) if name is NotImplemented else name
        )
        self.value = value

    def __setattr__(self, name, val):
        if hasattr(self, name):
            raise AttributeError("attribute %s is not writable" % name)
        return super(Marker, self).__setattr__(name, val)

    def __nonzero__(self):
        return bool(self.value)

    def __eq__(self, other):
        if not isinstance(other, Marker):
            return False
        return self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.name))

Marker.Undefined = Marker("undefined", None)
Marker.Missed = Marker("missed", None)
Marker.Disabled = Marker("disabled", None)

try:
    from ycyc.base.lazyutils import lazy_init

    class SimpleMarkers(object):
        @lazy_init
        def __getattr__(self, name):
            return Marker(name)
except ImportError:
    pass
