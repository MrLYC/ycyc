#!/usr/bin/env python
# encoding: utf-8

import contextlib
import logging.config
import logging


def quick_config(log_file="application.log"):
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
            '': {
                'handlers': ['console', 'file'],
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
    level, logging.root.manager.disable = logging.root.manager.disable, level
    try:
        yield
    finally:
        level, logging.root.manager.disable = logging.root.manager.disable, level


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
