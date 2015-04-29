#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.base import funcutils


class TestCoding(TestCase):
    b_en = b"test"
    b_ch = u"测试".encode("utf-8")
    u_en = u"test"
    u_ch = u"测试"

    def test_encode(self):
        self.assertEqual(self.b_en, funcutils.encode(self.u_en, "utf-8"))
        self.assertEqual(self.b_ch, funcutils.encode(self.u_ch, "utf-8"))
        self.assertEqual(self.b_en, funcutils.encode(self.b_en, "utf-8"))
        self.assertEqual(self.b_ch, funcutils.encode(self.b_ch, "utf-8"))

    def test_decode(self):
        self.assertEqual(self.u_en, funcutils.decode(self.u_en, "utf-8"))
        self.assertEqual(self.u_ch, funcutils.decode(self.u_ch, "utf-8"))
        self.assertEqual(self.u_en, funcutils.decode(self.b_en, "utf-8"))
        self.assertEqual(self.u_ch, funcutils.decode(self.b_ch, "utf-8"))

    def test_bytescat(self):
        target = u"test测试".encode("utf-8")
        self.assertEqual(funcutils.bytescat(self.b_en, self.b_ch), target)
        self.assertEqual(funcutils.bytescat(self.u_en, self.u_ch), target)
        self.assertEqual(funcutils.bytescat(self.b_en, self.u_ch), target)
        self.assertEqual(funcutils.bytescat(self.u_en, self.b_ch), target)

        target = u"测试测试".encode("utf-8")
        self.assertEqual(funcutils.bytescat(self.b_ch, self.b_ch), target)
        self.assertEqual(funcutils.bytescat(self.u_ch, self.u_ch), target)
        self.assertEqual(funcutils.bytescat(self.b_ch, self.u_ch), target)
        self.assertEqual(funcutils.bytescat(self.u_ch, self.b_ch), target)

    def test_strcat(self):
        target = u"test测试"
        self.assertEqual(funcutils.strcat(self.b_en, self.b_ch), target)
        self.assertEqual(funcutils.strcat(self.u_en, self.u_ch), target)
        self.assertEqual(funcutils.strcat(self.b_en, self.u_ch), target)
        self.assertEqual(funcutils.strcat(self.u_en, self.b_ch), target)

        target = u"测试测试"
        self.assertEqual(funcutils.strcat(self.b_ch, self.b_ch), target)
        self.assertEqual(funcutils.strcat(self.u_ch, self.u_ch), target)
        self.assertEqual(funcutils.strcat(self.b_ch, self.u_ch), target)
        self.assertEqual(funcutils.strcat(self.u_ch, self.b_ch), target)

        gbk_ch = u"测试".encode("gbk")
        self.assertEqual(
            funcutils.strcat(gbk_ch, self.b_ch, "gbk", "utf-8"), target)
        self.assertEqual(
            funcutils.strcat(gbk_ch, self.u_ch, "gbk", "utf-8"), target)
        self.assertEqual(
            funcutils.strcat(self.b_ch, gbk_ch, "utf-8", "gbk"), target)
        self.assertEqual(
            funcutils.strcat(self.u_ch, gbk_ch, "utf-8", "gbk"), target)
