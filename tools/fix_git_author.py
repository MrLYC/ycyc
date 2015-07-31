#!/usr/bin/env python
# encoding: utf-8

import argparse
import re
import six
import sys
import tempfile
from os import path as os_path
import os

from ycyc.base.adapter import main_entry
from ycyc.base.resources import Regex
from ycyc.base.filetools import cd, mk_not_existed_path, safe_open_for_write
from ycyc.base.shelltools import ShellCommands

FIXCMD_TEMPLATE = '''
#!/bin/sh

git filter-branch -f --env-filter '

OLD_EMAIL="{old_email}"
CORRECT_NAME="{new_author}"
CORRECT_EMAIL="{new_email}"

if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
export GIT_COMMITTER_NAME="$CORRECT_NAME"
export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
export GIT_AUTHOR_NAME="$CORRECT_NAME"
export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags
'''


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


def error_exit(msg, errno=-1):
    six.print_("[x]", msg)
    sys.exit(errno)


@main_entry
def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("repo", help="local git repo path")
    arg_parser.add_argument("email", help="email addr in history to filter")
    arg_parser.add_argument("author", help="new author name")
    arg_parser.add_argument("-m", "--new_email", help="new email addr")

    args = arg_parser.parse_args()
    if not Validater.is_avaliable_email(args.email):
        error_exit("%s is not a avaliable email address" % args.email)
    if not Validater.is_avaliable_repo(args.repo):
        error_exit("%s is not a avaliable repository path" % args.repo)
    new_email = args.new_email or args.email
    if not Validater.is_avaliable_email(new_email):
        error_exit("%s is not a avaliable email address" % new_email)

    with cd(args.repo):
        path = mk_not_existed_path("./fix_git_author.sh")
        with safe_open_for_write(path) as fp:
            try:
                fp.write(FIXCMD_TEMPLATE.format(
                    old_email=args.email,
                    new_author=args.author,
                    new_email=args.new_email,
                ))
                status = ShellCommands.sh.check_call(path)
                sys.exit(status)
            except Exception as err:
                error_exit(str(err), -2)
            finally:
                os.remove(path)
