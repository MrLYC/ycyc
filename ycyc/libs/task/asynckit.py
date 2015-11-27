#!/usr/bin/env python
# coding=utf-8


class AsyncResultProxy(object):
    def __init__(self, async_result):
        self._async_result = async_result

    def __getattr__(self, name):
        result = self._async_result.get()
        return getattr(self._async_result, name)
