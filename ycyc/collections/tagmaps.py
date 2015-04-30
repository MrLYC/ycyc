#!/usr/bin/env python
# encoding: utf-8


class TagMaps(dict):
    DefaultKey = ""

    def __missing__(self, key):
        if isinstance(key, int):
            return self.keys()[key]
        if self.DefaultKey in self:
            return self.get(self.DefaultKey)
        raise KeyError(key)

    def register(self, key, force=False):
        """
        Register obj as a decorator

        :param key: obj key
        :param force: force update
        """
        key = str(key)
        if not force and key in self:
            raise KeyError("%s was existed" % key)

        def update(obj):
            self.update(key, obj)
            return obj

        return update

    def update(self, key_or_dict, obj=NotImplemented):
        if obj is not NotImplemented:
            key_or_dict = {str(key_or_dict): obj}

        return super(TagMaps, self).update(key_or_dict)
