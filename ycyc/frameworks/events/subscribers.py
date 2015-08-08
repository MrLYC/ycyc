#!/usr/bin/env python
# encoding: utf-8

import threading


class BlockSubscriber(object):
    """
    Block until event happend
    """

    def __init__(self, checker=None):
        self.block_cond = threading.Condition()
        self.checker = checker or (lambda *a, **k: True)

    def __call__(self, *args, **kwg):
        if not self.checker(*args, **kwg):
            return
        with self.block_cond:
            self.block_cond.notify()

    def wait(self, timeout=None):
        """
        Wait until event happend
        """
        with self.block_cond:
            self.block_cond.wait(timeout)
