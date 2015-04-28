#!/usr/bin/env python
# encoding: utf-8

from contextlib import contextmanager
import six
import logging

logger = logging.getLogger(__name__)


@contextmanager
def catch(errors=Exception, reraise=None, callback=None):
    try:
        yield
    except errors as err:
        if callback:
            callback(err)
        if reraise:
            six.raise_from(reraise, err)


@contextmanager
def subprocessor(*args, **kwg):
    from subprocess import Popen
    processor = None
    try:
        processor = Popen(*args, **kwg)
        yield processor
    finally:
        if processor.poll() is None:
            processor.terminate()
            processor.wait()
