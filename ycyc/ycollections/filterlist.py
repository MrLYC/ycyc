#!/usr/bin/env python
# encoding: utf-8

from collections import deque


class FilterList(deque):
    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, list(self))

    def filter(self, func):
        """
        Return a new FilterList which filter by func
        """
        return self.__class__(filter(func, self))

    def exclude(self, func):
        """
        Return a new FilterList which exclude by func
        """
        return self.filter(lambda x: not func(x))

    def first(self, default=None):
        """
        Return the first item if existed, otherwise return default
        """
        return self[0] if self else default

    def last(self, default=None):
        """
        Return the last item if existed, otherwise return default
        """
        return self[-1] if self else default
