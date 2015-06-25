#!/usr/bin/env python
# encoding: utf-8

"""
A adapter tool module
"""

import collections


class ObjAsDictAdapter(collections.Mapping):
    """
    Provided a adapter that allow visit a object as dict
    """
    def __init__(self, obj):
        self.__object = obj

    def __getitem__(self, name):
        try:
            return getattr(self.__object, name)
        except AttributeError:
            raise KeyError(name)

    def __setitem__(self, name, value):
        setattr(self.__object, name, value)

    def __iter__(self):
        return iter(dir(self.__object))

    def __len__(self):
        return len(dir(self.__object))


class Marker(object):
    def __init__(self, name=NotImplemented):
        self.name = "Mark[%s]" % id(self) if name is NotImplemented else name
        self.__freezed = True

    def __setattr__(self, name, val):
        if getattr(self, "__freezed", False):
            raise AttributeError("attribute %s is not writable" % name)
        super(Marker, self).__setattr__(name, val)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, self.name)

Marker.Undefined = Marker("undefined")
Marker.Missed = Marker("missed")
Marker.Disabled = Marker("disabled")
