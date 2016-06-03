#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import mock

from ycyc.tests import mock_patches
from ycyc.base import filetools


class TestOserrorFormat(TestCase):
    def test_windows_env(self):
        with mock_patches("ycyc.base.filetools.exceptions") as patches:
            patches.exceptions.WindowsError = NotImplementedError

            @filetools.oserror_format
            def foo():
                raise patches.exceptions.WindowsError

            with self.assertRaises(OSError):
                foo()

    def test_linux_env(self):
        @filetools.oserror_format
        def foo():
            raise OSError

        with self.assertRaises(OSError):
            foo()


class TestDirHelper(TestCase):
    Path = "./lyc/"

    def test_make_sure_dir_exists(self):
        with mock_patches(
            "ycyc.base.filetools.os.path.exists",
            "ycyc.base.filetools.os.makedirs",
        ) as patches:
            patches.exists.return_value = True

            filetools.make_sure_dir_exists(self.Path)

            self.assertEqual(patches.exists.call_count, 1)
            self.assertEqual(patches.makedirs.call_count, 0)

        with mock_patches(
            "ycyc.base.filetools.os.path.exists",
            "ycyc.base.filetools.os.makedirs",
        ) as patches:
            patches.exists.return_value = False

            filetools.make_sure_dir_exists(self.Path)

            self.assertEqual(patches.exists.call_count, 1)
            self.assertEqual(patches.makedirs.call_count, 1)

    def test_remove_dir(self):
        with mock_patches(
            "ycyc.base.filetools.shutil.rmtree",
            "ycyc.base.filetools.os.removedirs",
        ) as patches:
            filetools.remove_dir(self.Path)

            self.assertEqual(patches.rmtree.call_count, 0)
            self.assertEqual(patches.removedirs.call_count, 1)

        with mock_patches(
            "ycyc.base.filetools.shutil.rmtree",
            "ycyc.base.filetools.os.removedirs",
        ) as patches:
            filetools.remove_dir(self.Path, True)

            self.assertEqual(patches.rmtree.call_count, 1)
            self.assertEqual(patches.removedirs.call_count, 0)

    def test_make_sure_dir_empty(self):
        with mock_patches(
            "ycyc.base.filetools.os.path.exists",
            "ycyc.base.filetools.make_sure_dir_exists",
        ) as patches:
            patches.exists.return_value = False

            filetools.make_sure_dir_empty(self.Path)

            patches.exists.assert_called_once_with(self.Path)
            patches.make_sure_dir_exists.assert_called_once_with(self.Path)

        with mock_patches(
            "ycyc.base.filetools.os.path.exists",
            "ycyc.base.filetools.os.listdir",
            "ycyc.base.filetools.os.path.isdir",
            "ycyc.base.filetools.remove_dir",
            "ycyc.base.filetools.os.remove",
        ) as patches:
            patches.exists.return_value = True
            patches.listdir.return_value = ["a", "b/"]
            patches.isdir.side_effect = lambda f: f.endswith("/")

            filetools.make_sure_dir_empty(self.Path)

            patches.exists.assert_called_once_with(self.Path)
            patches.listdir.assert_called_once_with(self.Path)
            patches.remove.assert_called_once_with(self.Path + "a")
            patches.remove_dir.assert_called_once_with(self.Path + "b/")

    def test_make_sure_not_exists(self):
        with mock_patches(
            "ycyc.base.filetools.os.path.exists",
        ) as patches:
            patches.exists.return_value = False

            filetools.make_sure_not_exists(self.Path)

            patches.exists.assert_called_once_with(self.Path)

        with mock_patches(
            "ycyc.base.filetools.os.path.exists",
            "ycyc.base.filetools.os.path.isdir",
            "ycyc.base.filetools.remove_dir",
        ) as patches:
            patches.exists.return_value = True
            patches.isdir.return_value = True

            filetools.make_sure_not_exists(self.Path)

            patches.exists.assert_called_once_with(self.Path)
            patches.isdir.assert_called_once_with(self.Path)
            patches.remove_dir.assert_called_once_with(self.Path, recursion=True)

        with mock_patches(
            "ycyc.base.filetools.os.path.exists",
            "ycyc.base.filetools.os.path.isdir",
            "ycyc.base.filetools.os.remove",
        ) as patches:
            patches.exists.return_value = True
            patches.isdir.return_value = False

            filetools.make_sure_not_exists(self.Path)

            patches.exists.assert_called_once_with(self.Path)
            patches.isdir.assert_called_once_with(self.Path)
            patches.remove.assert_called_once_with(self.Path)


class TestChangeDir(TestCase):
    Path = "./lyc/"

    def test_usage(self):
        with mock_patches(
            "ycyc.base.filetools.os.chdir",
        ) as patches:
            with filetools.cd(self.Path):
                self.assertEqual(patches.chdir.call_count, 1)

            self.assertEqual(patches.chdir.call_count, 2)

    def test_exception(self):
        with mock_patches(
            "ycyc.base.filetools.os.chdir",
        ) as patches:
            with self.assertRaises(NotImplementedError):
                with filetools.cd(self.Path):
                    self.assertEqual(patches.chdir.call_count, 1)
                    raise NotImplementedError

            self.assertEqual(patches.chdir.call_count, 2)
