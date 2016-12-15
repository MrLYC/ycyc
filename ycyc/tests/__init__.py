#!/usr/bin/env python
# encoding: utf-8

from contextlib import contextmanager

import mock

__author__ = 'Liu Yicong'
__email__ = 'imyikong@gmail.com'


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
    mock_patches = []
    mocks = mock.Mock()

    for k, i in zip(attrs, patches):
        patch = mock.patch(i)
        mock_patches.append(patch)
        setattr(mocks, k, patch.start())

    try:
        yield mocks
    finally:
        for p in mock_patches:
            p.stop()
