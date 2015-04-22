#!/usr/bin/env python
# encoding: utf-8

import collections
from ycyc.base.itertool import getfirst


class GenData(collections.Mapping):
    def __init__(self, base, extend=None):
        self.base_data = base
        self.extend_data = extend
        self.real_keys = base.viewkeys() | extend.viewkeys()

    def __getitem__(self, key):
        if key in self.extend_data:
            return self.extend_data[key]
        return self.base_data[key]

    def __iter__(self):
        return iter(self.real_keys)

    def __len__(self):
        return len(self.real_keys)


class TxtGenerator(object):
    ITEM_SEP = ""
    NEWLINE_SEP = "\n"

    def __init__(self, data):
        self.output_lst = collections.deque()
        self.data = data

    def write(self, txt, **extend_data):
        data = GenData(self.data, extend_data)
        self.output_lst.append(txt.format(**data))

    def writeline(self, txt, **extend_data):
        self.write(txt + self.NEWLINE_SEP, **extend_data)

    def prepare(self):
        txt = self.ITEM_SEP.join(self.output_lst)
        self.output_lst.clear()
        self.output_lst.append(txt)

    def getval(self):
        self.prepare()
        return getfirst(self.output_lst)
