#!/usr/bin/env python
# encoding: utf-8

import os
import codecs
import tempfile
import shutil
from contextlib import contextmanager
import exceptions
from functools import wraps
import hashlib

from ycyc.base import contextutils


def oserror_format(func):
    """
    Decorator that catch WindowsError and reraise it as OSError
    """
    @wraps(func)
    def foo(*args, **kwargs):
        with contextutils.catch(
            getattr(exceptions, "WindowsError", OSError),
            reraise=OSError,
        ):
            return func(*args, **kwargs)
    return foo


@oserror_format
def make_sure_dir_exists(path):
    """
    Create the directories when the path is not exists.

    :param path: path string
    """
    if not os.path.exists(path):
        os.makedirs(path)


@oserror_format
def remove_dir(path, recursion=False):
    """
    Remove the directory.

    :param path: path string
    :param recursion: if delete sub directories and files
    """
    if recursion:
        shutil.rmtree(path)
    else:
        os.removedirs(path)


@oserror_format
def make_sure_dir_empty(path):
    """
    Make sure the directory is empty.

    :param path: path string
    """
    if not os.path.exists(path):
        make_sure_dir_exists(path)
    else:
        for i in os.listdir(path):
            i_path = os.path.join(path, i)
            if os.path.isdir(i_path):
                remove_dir(i_path)
            else:
                os.remove(i_path)


@oserror_format
def make_sure_not_exists(path):
    """
    Make sure the path is not exists.

    :param path: path string
    """
    if not os.path.exists(path):
        return
    if os.path.isdir(path):
        remove_dir(path, recursion=True)
    else:
        os.remove(path)


def safe_open_for_write(fn, encoding="utf-8"):
    """
    Auto create the directories and open a file for write(w+).

    :param fn: file path string
    :param encoding: file encoding
    """
    make_sure_dir_exists(os.path.dirname(fn))
    return codecs.open(fn, "w+", encoding)


def touch_file(path):
    """
    As same as *nix command `touch`

    :param path: path string
    """
    with safe_open_for_write(path):
        pass


def safe_open_for_update(fn, encoding="utf-8"):
    """
    Make sure open a file for update(r+).

    :param fn: file path string
    :param encoding: file encoding
    """
    if not os.path.exists(fn):
        return safe_open_for_write(fn, encoding)
    return codecs.open(fn, "r+", encoding)


def safe_open_for_read(fn, encoding="utf-8"):
    """
    Make sure open a file for read(r).

    :param fn: file path string
    :param encoding: file encoding
    """
    if os.path.exists(fn):
        return codecs.open(fn, "r", encoding)
    return tempfile.TemporaryFile("r")


@contextmanager
@oserror_format
def cd(path):
    """
    Switch to a directory to excute.

    :param path: directory string
    """
    current_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        with contextutils.catch():
            os.chdir(current_dir)


def bytes_from(path):
    """
    Return the bytes from a file.

    :param path: file path string
    """
    with open(path, "rb") as fp:
        return fp.read()


def text_from(path, encoding="utf-8"):
    """
    Return the text from a file.

    :param path: file path string
    :param encoding: file encoding
    """
    with codecs.open(path, "r", encoding) as fp:
        return fp.read()


def hash_of(path, hash_name):
    """
    Return the hash of a file

    :param path: file path string
    :param hash_name: hash algorithm name(md5/sha1/sha256/sha512)
    """
    hash = hashlib.new(hash_name, bytes_from(path))
    return hash.hexdigest()


def sha1_of(path):
    """
    Return the sha1 hash of a file

    :param path: file path string
    """
    return hash_of(path, "sha1")


def md5_of(path):
    """
    Return the md5 hash of a file

    :param path: file path string
    """
    return hash_of(path, "md5")
