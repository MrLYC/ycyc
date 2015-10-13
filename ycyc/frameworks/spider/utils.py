#!/usr/bin/env python
# encoding: utf-8


def save_to(path, data, mode="ab"):
    with open(path, mode) as fp:
        fp.write(data)


def flow_return():
    raise StopIteration
