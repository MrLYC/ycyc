#!/usr/bin/env python
# encoding: utf-8

import re

from ycyc.base.adapter import main_entry
from ycyc.base.shelltools import ShellCommands


@main_entry
def main():
    paths = re.findall(
        r"^(?:\s+(?:modified|new file):\s*)(.*?)(?:\s*)$",
        ShellCommands.git.check_output("status"),
        re.M
    )
    if not paths:
        return -1

    return sum(map(
        lambda x: ShellCommands.dos2unix.check_call(str(x)),
        set(paths),
    ))
