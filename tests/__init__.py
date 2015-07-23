#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Liu Yicong'
__email__ = 'imyikong@gmail.com'

from contextlib import contextmanager, nested

import mock


@contextmanager
def mock_patches(*patches, **named_patches):
    """
    A context manager to help create mock patches.
    >>> with mock_patches("package.module.cls", cls2="package.cls") as mocks:
    ...     mocks.cls() #=> package.module.cls
    ...     mocks.cls2() #=> package.cls
    """
    attrs = list(i.split(".")[-1] for i in patches)
    attrs.extend(named_patches.keys())
    patches = list(patches)
    patches.extend(named_patches.values())
    mocks = mock.Mock()

    with nested(*map(mock.patch, patches)) as mp:
        for k, m in zip(attrs, mp):
            setattr(mocks, k, m)

        yield mocks
