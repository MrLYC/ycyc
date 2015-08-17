#!/usr/bin/env python
# encoding: utf-8

import subprocess

from ycyc.base import decoratorutils
from ycyc.base import contextutils


class Command(object):
    @classmethod
    def subprocess_args(cls, name, cmd_args, popen_kwargs):
        cmds = [name]
        cmds.extend(map(str, cmd_args))
        popen_kwargs.setdefault("shell", False)
        return cmds, popen_kwargs

    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        cmds, kwargs = self.subprocess_args(self.name, args, kwargs)
        return subprocess.Popen(cmds, **kwargs)

    def check_call(self, *args, **kwargs):
        cmds, kwargs = self.subprocess_args(self.name, args, kwargs)
        return subprocess.check_call(cmds, **kwargs)

    def check_output(self, *args, **kwargs):
        cmds, kwargs = self.subprocess_args(self.name, args, kwargs)
        return subprocess.check_output(cmds, **kwargs)

    def subprocessor(self, *args, **kwargs):
        cmds, kwargs = self.subprocess_args(self.name, args, kwargs)
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.PIPE)

        return contextutils.subprocessor(cmds, **kwargs)


@decoratorutils.call_immediately()
class ShellCommands(object):
    """
    >>> ShellCommands.echo("hello lyc")
    hello lyc
    """
    def __getattr__(self, name):
        return Command(name)
