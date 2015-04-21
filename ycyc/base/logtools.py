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
    """disable logger
    """
    logging.disable(level)
    yield
    logging.disable(logging.NOTSET)
