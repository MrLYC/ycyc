#!/usr/bin/env python
# encoding: utf-8

import contextlib
import logging.config
import logging
import sys
import thread
import inspect

logger = logging.getLogger(__name__)


class LoggerInfo(object):
    def __init__(self, frame=None):
        if frame is None:
            frames = sys._current_frames()
            frame = frames[thread.get_ident()]
            self.frame = frame.f_back
        else:
            self.frame = frame

    @property
    def line_no(self):
        return self.frame.f_lineno

    @property
    def code_name(self):
        return self.frame.f_code.co_name

    @property
    def is_top_frame(self):
        if self.frame.f_back is None:
            return True
        return False

    @property
    def func_args(self):
        args = inspect.getargvalues(self.frame)
        code_locals = args.locals
        result = {
            i: code_locals[i]
            for i in args.args
        }
        if args.varargs:
            result[args.varargs] = code_locals[args.varargs]
        if args.keywords:
            result[args.keywords] = code_locals[args.keywords]
        return result


def quick_config(log_file="application.log", loggers=()):
    """
    a quick config for logging

    :param log_file: the file for file handler
    """
    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
                'datefmt': '[%d/%b/%Y %H:%M:%S]',
            },
            'simple': {
                'format': '%(asctime)s %(levelname)s %(name)s:%(lineno)s %(message)s',
                'datefmt': '[%d/%b/%Y %H:%M:%S]',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': log_file,
                'formatter': 'verbose'
            },
        },
        'loggers': {
            name: {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
            }
            for name in loggers or [""]
        },
    }
    logging.config.dictConfig(config)


def console_only_config(level='DEBUG', format='%(message)s'):
    config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'simple': {
                'format': format,
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
            },
        },
    }
    logging.config.dictConfig(config)


@contextlib.contextmanager
def log_disable(level=logging.CRITICAL):
    """
    A context manager to disable all logging calls of
    severity 'level' and below in block
    """
    cur_frames = sys._current_frames()
    cur_frame = cur_frames[thread.get_ident()]
    pre_frame = cur_frame.f_back

    logger.info(
        "with logger disabled from %s to %s in %s[%s], id: %s",
        logging.root.manager.disable, level,
        pre_frame.f_code.co_name, pre_frame.f_lineno,
        id(cur_frame),
    )

    level, logging.root.manager.disable = logging.root.manager.disable, level
    try:
        yield
    finally:
        level, logging.root.manager.disable = logging.root.manager.disable, level

        logger.info("logger reseted, id: %s", id(cur_frame))


def log_with_label(log_method, label):
    """
    >>> logger_waring = log_with_label(logger.waring, "waring: %s")
    >>> try:
    ...     may_raise_exception()
    ... except Exception as err:
    ...     logger_waring(err)

    :param log_method: method of a logger to pack
    :param label: label pass to log_method as the first argument
    :return: logger method packed method
    """
    import functools

    @functools.wraps(log_method)
    def logger_method(*args, **kwargs):
        return log_method(label, *args, **kwargs)

    return logger_method


class LogFunctionCall(object):
    def __init__(self, func=None, args=None, kwargs=None, returned=None):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.returned = returned

    def __str__(self):
        s_returned = (
            "" if self.returned is None
            else "-> %s" % str(self.returned)
        )

        args = map(str, self.args or ())
        args.extend(
            "{k}={v}".format(k=str(k), v=str(v))
            for k, v in self.kwargs.items() or ()
        )

        return "{f}({args}){returned}".format(
            f=self.func.__name__ if self.func else "",
            args=", ".join(args),
            returned="" if self.returned is None
            else "-> %s" % str(self.returned)
        )
