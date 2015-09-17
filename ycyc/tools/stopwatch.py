#!/usr/bin/env python
# encoding: utf-8

import time


class Stopwatch(object):
    """
    A sadness timer
    """
    def __init__(self):
        self.start_on = None
        self._duration = 0
        self._enable = False

    @property
    def enable(self):
        return self._enable

    @enable.setter
    def enable(self, val):
        if val:
            self.start_on = time.time()
            self._enable = True
        else:
            self._duration = self.duration
            self._enable = False

    @property
    def duration(self):
        if self.enable:
            return time.time() - self.start_on + self._duration
        return self._duration

    def __enter__(self):
        self.enable = True
        return self

    def __exit__(self, typ, val, trbk):
        self.enable = False
