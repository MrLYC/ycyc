#!/usr/bin/env python
# encoding: utf-8

import argparse
import os
import six

from ycyc.base.txtutils import drop_prefix
from ycyc.base.adapter import main_entry


class FileExisted(Exception):
    pass

TeseCaseTemplate = '''
#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase


class {test_name}(TestCase):
    def test_usage(self):
        pass
'''.lstrip()

PackageInitModule = '''
#!/usr/bin/env python
# encoding: utf-8
__author__ = "LYC"
'''.lstrip()


def is_script_file(file):
    return os.path.isfile(file) and file.endswith(".py")


def get_all_scripts(path, recursion=0):
    if is_script_file(path):
        return [path]

    results = []
    if os.path.isdir(path):
        for f in os.listdir(path):
            f_path = os.path.join(path, f)
            if is_script_file(f_path):
                results.append(f_path)
            elif recursion:
                results.extend(get_all_scripts(f_path, recursion - 1))
    return results


def try_init_package(dir_name):
    init_module = os.path.join(dir_name, "__init__.py")

    if not os.path.exists(init_module):
        os.mkdir(dir_name)
        with open(init_module, "wt") as fp:
            fp.write(PackageInitModule)


def make_test_dirs(dir_name):
    if os.path.exists(dir_name):
        return

    dir_name = dir_name.rstrip(os.sep)
    parent_dir = os.path.dirname(dir_name.rstrip(os.sep))
    make_test_dirs(parent_dir)
    os.mkdir(dir_name)
    try_init_package(dir_name)


def mk_unittest_script(script_relative_path, root):
    path, script = os.path.split(script_relative_path)
    real_dir = os.path.join(root, path)
    real_path = os.path.join(real_dir, "test_%s" % script)
    module_name, _ = os.path.splitext(script)

    try_init_package(real_dir)

    make_test_dirs(real_dir)
    if os.path.exists(real_path):
        raise FileExisted(real_path)


    with open(real_path, "wt") as fp:
        fp.write(TeseCaseTemplate.format(
            test_name=(
                "Test%s" % module_name.title().replace("_", "")
            ),
        ))


@main_entry
def main():
    working_dir = os.getcwd()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("path")
    arg_parser.add_argument(
        "-r", "--recursion", default=0, type=int,
    )
    arg_parser.add_argument(
        "-a", "--anchor", default=working_dir,
    )
    arg_parser.add_argument(
        "-t", "--target",
        default=os.path.join(working_dir, "tests"),
    )
    args = arg_parser.parse_args()

    for p in get_all_scripts(args.path, args.recursion):
        dir_path, file = os.path.split(p)
        if file.startswith("__"):
            continue
        try:
            if args.anchor:
                p = drop_prefix(p, args.anchor)
            mk_unittest_script(p, args.target)
        except FileExisted as err:
            six.print_("file is existed:", err)
