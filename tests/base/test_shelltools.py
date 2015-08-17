#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

import mock

from tests import mock_patches
from ycyc.base import shelltools


class TestCommands(TestCase):
    def test_shell_commands_usage(self):
        self.assertIsInstance(shelltools.ShellCommands, object)
        command = shelltools.ShellCommands.echo
        self.assertIsInstance(command, shelltools.Command)
        self.assertIsInstance(command, shelltools.Command)
        self.assertEqual(command.name, "echo")

    def test_command_usage(self):
        with mock_patches(
            "ycyc.base.shelltools.subprocess.Popen",
            "ycyc.base.shelltools.subprocess.check_call",
            "ycyc.base.shelltools.subprocess.check_output",
            "ycyc.base.shelltools.contextutils.subprocessor",
        ) as patches:
            patches.check_call.return_value = 0
            patches.check_output.return_value = "hello lyc"

            command = shelltools.Command("echo")

            self.assertEqual(
                command.check_output("hello", "lyc"),
                patches.check_output.return_value
            )
            patches.check_output.assert_call_with("hello", "lyc")

            self.assertEqual(
                command.check_call("lyc"),
                patches.check_call.return_value
            )
            patches.check_call.assert_call_with("lyc")

            self.assertIs(
                command("hello", "lyc"),
                patches.Popen.return_value
            )

            subprocessor = command.subprocessor("hello", "lyc")
            subprocessor.assert_call_with(
                "hello", "lyc",
                stdout=shelltools.subprocess.PIPE,
                stderr=shelltools.subprocess.PIPE,
            )
