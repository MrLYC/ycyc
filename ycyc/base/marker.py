#!/usr/bin/env python
# encoding: utf-8


class Marker(object):
    def __init__(self, name=NotImplemented):
        self.name = "Mark[%s]" % id(self) if name is NotImplemented else name
        self.__freezed = True

    def __setattr__(self, name, val):
        if getattr(self, "__freezed", False):
            raise AttributeError("attribute %s is not writable" % name)
        super(Marker, self).__setattr__(name, val)

    def __eq__(self, other):
        if not isinstance(other, Marker):
            return False
        return self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.name))

Marker.Undefined = Marker("undefined")
Marker.Missed = Marker("missed")
Marker.Disabled = Marker("disabled")

try:
    from ycyc.base.lazyutils import lazy_init

    class SimpleMarkers(object):
        @lazy_init
        def __getattr__(self, name):
            return Marker(name)
except ImportError:
    pass
