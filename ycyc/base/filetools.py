#!/usr/bin/env python
# encoding: utf-8

import os
from os import path as os_path
import codecs
import tempfile
import shutil
from contextlib import contextmanager
import exceptions
from functools import wraps
import hashlib
from datetime import datetime
import re

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
    if not os_path.exists(path):
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
    if not os_path.exists(path):
        make_sure_dir_exists(path)
    else:
        for i in os.listdir(path):
            i_path = os_path.join(path, i)
            if os_path.isdir(i_path):
                remove_dir(i_path)
            else:
                os.remove(i_path)


@oserror_format
def make_sure_not_exists(path):
    """
    Make sure the path is not exists.

    :param path: path string
    """
    if not os_path.exists(path):
        return
    if os_path.isdir(path):
        remove_dir(path, recursion=True)
    else:
        os.remove(path)


def safe_open_for_write(fn, encoding="utf-8"):
    """
    Auto create the directories and open a file for write(w+).

    :param fn: file path string
    :param encoding: file encoding
    """
    make_sure_dir_exists(os_path.dirname(fn))
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
    if not os_path.exists(fn):
        return safe_open_for_write(fn, encoding)
    return codecs.open(fn, "r+", encoding)


def safe_open_for_read(fn, encoding="utf-8"):
    """
    Make sure open a file for read(r).

    :param fn: file path string
    :param encoding: file encoding
    """
    if os_path.exists(fn):
        return codecs.open(fn, "r", encoding)
    return tempfile.TemporaryFile("r")


def choice_one_if_exists(paths, default=None):
    """
    Choice the first path in paths which is exists.
    You can use this to choice application configuration files.
    Example:
        there are some configuration files:
            /etc/conf/lyc.conf -> for production
            ~/conf/lyc.debug.conf -> for developing
            ./conf/demo.conf -> for default configuration
        so you can put you real configuration files to this places
        to identify your real environment for this application.

    >>> real_conf = choice_one_if_exists([
    ...     "/etc/conf/lyc.conf",
    ...     "~/conf/lyc.conf",
    ...     "./conf/demo.conf",
    ... ])

    :param fn: file path string
    :param encoding: file encoding
    """
    isexists = os_path.exists
    for p in paths:
        if isexists(p):
            return p
    return default


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


def available_file_name(name, replaces="_"):
    """
    Return a available file name that replace some forbidden chars

    :param name: file name
    :param replaces: replaces char
    """
    return re.sub(
        r"[\<\>/\\\|:\"\*\?]",
        replaces,
        name,
    )


def mk_not_existed_path(path):
    """
    Return a new file name based on path, and make sure the new name
    is not existed.

    :param path: file name
    """
    name_without_ext, ext = os_path.splitext(path)

    n = 1
    while os_path.exists(path):
        n += 1
        path = name_without_ext + "(%d)" % n + ext

    return path


class PathInfo(object):
    def __init__(self, path):
        self.path = os_path.realpath(path)

    def __str__(self):
        return "<{cls}: {path}>".format(
            cls=self.__class__.__name__,
            path=self.path,
        )

    def __repr__(self):
        return "{cls}('{path}')".format(
            cls=self.__class__.__name__,
            path=self.path,
        )

    @property
    def is_exists(self):
        return os_path.exists(self.path)

    @property
    def is_file(self):
        return os_path.isfile(self.path)

    @property
    def is_dir(self):
        return os_path.isdir(self.path)

    @property
    def is_link(self):
        return os_path.islink(self.path)

    @property
    def dir_path(self):
        return os_path.dirname(self.path)

    @property
    def directory(self):
        return PathInfo(self.dir_path)

    @property
    def children(self):
        if not self.is_dir:
            return []
        return [
            PathInfo(os_path.join(self.path, i))
            for i in os.listdir(self.path)
        ]

    @property
    def full_name(self):
        dir, name = os_path.split(self.path)
        return name

    @property
    def name(self):
        name, ext = os_path.splitext(self.full_name)
        return name

    @property
    def extension(self):
        name, ext = os_path.splitext(self.full_name)
        return ext

    @property
    def stat(self):
        return os.stat(self.path)

    @property
    def length(self):
        return self.stat.st_size

    @property
    def last_access_timestamp(self):
        return self.stat.st_atime

    @property
    def last_access_time(self):
        return datetime.fromtimestamp(self.last_access_timestamp)

    @property
    def last_write_timestamp(self):
        return self.stat.st_mtime

    @property
    def last_write_time(self):
        return datetime.fromtimestamp(self.last_write_timestamp)

    @property
    def creation_timestamp(self):
        return self.stat.st_ctime

    @property
    def creation_time(self):
        return datetime.fromtimestamp(self.creation_timestamp)
