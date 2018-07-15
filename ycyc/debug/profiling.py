#!/usr/bin/env python
# encoding: utf-8

from functools import wraps
import cProfile
import pstats
from six import StringIO
from collections import namedtuple
from contextlib import contextmanager
import logging

ProfileStats = namedtuple("ProfileStats", ["profile", "output"])
logger = logging.getLogger(__name__)


@contextmanager
def enable_profiling(sort_by=None):
    profile = cProfile.Profile()
    output = StringIO.StringIO()
    profile.enable()
    try:
        yield ProfileStats(profile, output)
    finally:
        profile.disable()
        stats = pstats.Stats(profile, stream=output)
        stats.sort_stats(sort_by or "cumulative")
        stats.print_stats()


def function_profiling(sort_by=None, callback=logger.debug):
    def profiling_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with enable_profiling(sort_by) as stats:
                result = func(*args, **kwargs)
            callback(stats.output.getvalue())
            return result
        return wrapper
    return profiling_wrapper
