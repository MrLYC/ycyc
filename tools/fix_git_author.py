#!/usr/bin/env python
# encoding: utf-8

import sys
import os
from os import path as os_path
sys.path.append(os_path.dirname(os_path.dirname(__file__)))

import argparse
import re
from textwrap import dedent
import logging
from subprocess import CalledProcessError

from ycyc.base.adapter import main_entry
from ycyc.base.resources import Regex
from ycyc.base.filetools import cd
from ycyc.base.shelltools import ShellCommands
from ycyc.base.typeutils import constants
from ycyc.base.logutils import console_only_config

console_only_config()
logger = logging.getLogger(__name__)
ErrorNo = constants(
    UserErr=-1,
    EnvErr=-2,
    SysErr=-3,
    UnknownErr=-4,
)


class Validater(object):
    EmailRex = re.compile("^%s$" % Regex.email_addr())

    @classmethod
    def is_avaliable_email(cls, email):
        return cls.EmailRex.search(email) is not None

    @classmethod
    def is_avaliable_repo(cls, path):
        if not path:
            return False
        if not os_path.isdir(path):
            return False
        if not os_path.isdir(os_path.join(path, ".git")):
            return False
        return True


@main_entry
def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("repo", help="local git repo path")
    arg_parser.add_argument("email", help="email addr in history to filter")
    arg_parser.add_argument("author", help="new author name")
    arg_parser.add_argument("-m", "--new_email", help="new email addr")

    args = arg_parser.parse_args()
    if not Validater.is_avaliable_email(args.email):
        logger.error("[*] %s is not a avaliable email address", args.email)
        return ErrorNo.UserErr
    if not Validater.is_avaliable_repo(args.repo):
        logger.error("[*] %s is not a avaliable repository path", args.repo)
        return ErrorNo.UserErr
    new_email = args.new_email or args.email
    if not Validater.is_avaliable_email(new_email):
        logger.error("[*] %s is not a avaliable email address", new_email)
        return ErrorNo.UserErr

    with cd(args.repo):
        logger.info("[-] change directory to: %s" % os.getcwd())
        try:
            return ShellCommands.git.check_call(
                "filter-branch", "-f", "--env-filter",
                dedent("""
                    if [ "$GIT_COMMITTER_EMAIL" = "{old_email}" ]; then
                        export GIT_COMMITTER_NAME="{new_author}"
                        export GIT_COMMITTER_EMAIL="{new_email}"
                    fi
                    if [ "$GIT_AUTHOR_EMAIL" = "{old_email}" ]; then
                        export GIT_AUTHOR_NAME="{new_author}"
                        export GIT_AUTHOR_EMAIL="{new_email}"
                    fi""".format(
                    old_email=args.email,
                    new_author=args.author,
                    new_email=new_email,
                )),
                "--tag-name-filter", "cat", "--",
                "--branches", "--tags"
            )
        except CalledProcessError as err:
            logger.error("[x] returned code of git: %s", err.returncode)
            return ErrorNo.EnvErr
        except Exception as err:
            logger.error("[?] %s", str(err))
            return ErrorNo.UnknownErr
