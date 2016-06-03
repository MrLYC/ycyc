#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import mock

from ycyc.tests import mock_patches
from ycyc.base import shelltools


class TestCommands(TestCase):
    def test_shell_commands_usage(self):
        self.assertIsInstance(shelltools.ShellCommands, object)
        command = shelltools.ShellCommands.echo  # pylint: disable=E1101
        self.assertIsInstance(command, shelltools.Command)
        self.assertIsInstance(command, shelltools.Command)
        self.assertEqual(command.name, "echo")

    def test_check_output(self):
        with mock_patches(
            "ycyc.base.shelltools.subprocess.check_output",
        ) as patches:
            patches.check_output.return_value = "hello lyc"

            command = shelltools.Command("echo")

            self.assertEqual(
                command.check_output("hello", "lyc"),
                patches.check_output.return_value
            )
            call_args = patches.check_output.call_args[0]
            self.assertListEqual(call_args[0], ["echo", "hello", "lyc"])

    def test_check_call(self):
        with mock_patches(
            "ycyc.base.shelltools.subprocess.check_call",
        ) as patches:
            patches.check_call.return_value = 0

            command = shelltools.Command("echo")

            self.assertEqual(
                command.check_call("lyc"),
                patches.check_call.return_value
            )
            call_args = patches.check_call.call_args[0]
            self.assertListEqual(call_args[0], ["echo", "lyc"])

    def test_call(self):
        with mock_patches(
            "ycyc.base.shelltools.subprocess.Popen",
        ) as patches:
            command = shelltools.Command("echo")

            self.assertIs(
                command("hello", "lyc"),
                patches.Popen.return_value
            )

    def test_subprocessor(self):
        with mock_patches(
            "subprocess.Popen",
        ) as patches:
            command = shelltools.Command("echo")

            with command.subprocessor("hello", "lyc") as subprocessor:
                patches.Popen.assert_called_once_with(
                    ["echo", "hello", "lyc"],
                    stdout=shelltools.subprocess.PIPE,
                    stderr=shelltools.subprocess.PIPE,
                    shell=False,
                )
