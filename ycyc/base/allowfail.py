#!/usr/bin/env python
# encoding: utf-8
"""
AllowFail is a tool that you can use it to catch the exceptions for
a block as a context manager or a function as a decorator.
"""

import logging
from collections import namedtuple
from functools import wraps

__all__ = ("AllowFailResult", "AllowFail")
AllowFailResult = namedtuple("AllowFailResult", ["result", "exception"])


class AllowFail(object):
    """
    As a context manager:
    >>> with AllowFail("not important block"):
    ...     not_important_operator()

    As a decorator:
    >>> @AllowFail("not important function")
    ... def not_important_function():
    ...     pass
    It will packing the function returned result as AllowFailResult.
    AllowFailResult is a subclass of tuple which the first item is
    the real result of function call(set None when crashed) and the
    second item is the catched exception (set None when success).
    Call example:
    >>> result, exception = not_important_function()
    ... if exception is not None:
    ...     do_rockball_operator()

    >>> result = not_important_function()
    >>> if result.exception is not None:
    ...     do_rockball_operator()
    """
    logger = logging.getLogger("AllowFail")

    def __init__(self, label, on_error=None, logger=None, exc_info=False):
        """
        AllowFail constructor
        :param label: label pass to error_handler
        :param on_error: error_handler(default: AllowFail.on_error)
        :param logger: logger used in AllowFail.on_error
        :param exc_info: indicate AllowFail.on_error if log the execute info
        """
        self.label = label
        self.error_handler = on_error or self.on_error
        self.logger = logger or self.logger
        self.exc_info = exc_info

    def on_error(self, label, err):
        """
        Default on error handler
        :param label: label for logger
        :param err: exception
        """
        self.logger.warning("%s: %s", label, err, exc_info=self.exc_info)

    def __enter__(self):
        """
        Use instance as a context manager to protect a block
        :return: self
        """
        return self

    def __exit__(self, typ, val, trbk):
        """
        Catch exceptions
        :param typ: excrption type
        :param val: excrption
        :param trbk: traceback
        :return: True for catch
        """
        if typ:
            if val is None:
                val = typ()
            self.error_handler(self.label, val)

        # catch exceptions
        return True

    def __call__(self, func):
        """
        Use instance as a decorator to protect a function call
        :param func: function
        :return: protect function wrapper
        """
        @wraps(func)
        def protect(*args, **kwg):
            try:
                exception = None
                result = func(*args, **kwg)
            except Exception as err:
                exception = err
                result = None

            if exception:
                f_name = str(func)
                if hasattr(func, "__name__"):
                    f_name = func.__name__
                elif hasattr(func, "func_name"):
                    f_name = func.func_name
                else:
                    f_name = str(func)

                with AllowFail(
                        "On error handler %s" % f_name,
                        logger=self.logger, exc_info=self.exc_info):
                    self.error_handler(self.label, err)

            return AllowFailResult(result=result, exception=exception)
        return protect
