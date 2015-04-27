#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.base import functool


class TestCoding(TestCase):
    b_en = b"test"
    b_ch = u"测试".encode("utf-8")
    u_en = u"test"
    u_ch = u"测试"

    def test_encode(self):
        self.assertEqual(self.b_en, functool.encode(self.u_en, "utf-8"))
        self.assertEqual(self.b_ch, functool.encode(self.u_ch, "utf-8"))
        self.assertEqual(self.b_en, functool.encode(self.b_en, "utf-8"))
        self.assertEqual(self.b_ch, functool.encode(self.b_ch, "utf-8"))

    def test_decode(self):
        self.assertEqual(self.u_en, functool.decode(self.u_en, "utf-8"))
        self.assertEqual(self.u_ch, functool.decode(self.u_ch, "utf-8"))
        self.assertEqual(self.u_en, functool.decode(self.b_en, "utf-8"))
        self.assertEqual(self.u_ch, functool.decode(self.b_ch, "utf-8"))

    def test_bytescat(self):
        target = u"test测试".encode("utf-8")
        self.assertEqual(functool.bytescat(self.b_en, self.b_ch), target)
        self.assertEqual(functool.bytescat(self.u_en, self.u_ch), target)
        self.assertEqual(functool.bytescat(self.b_en, self.u_ch), target)
        self.assertEqual(functool.bytescat(self.u_en, self.b_ch), target)

        target = u"测试测试".encode("utf-8")
        self.assertEqual(functool.bytescat(self.b_ch, self.b_ch), target)
        self.assertEqual(functool.bytescat(self.u_ch, self.u_ch), target)
        self.assertEqual(functool.bytescat(self.b_ch, self.u_ch), target)
        self.assertEqual(functool.bytescat(self.u_ch, self.b_ch), target)

    def test_strcat(self):
        target = u"test测试"
        self.assertEqual(functool.strcat(self.b_en, self.b_ch), target)
        self.assertEqual(functool.strcat(self.u_en, self.u_ch), target)
        self.assertEqual(functool.strcat(self.b_en, self.u_ch), target)
        self.assertEqual(functool.strcat(self.u_en, self.b_ch), target)

        target = u"测试测试"
        self.assertEqual(functool.strcat(self.b_ch, self.b_ch), target)
        self.assertEqual(functool.strcat(self.u_ch, self.u_ch), target)
        self.assertEqual(functool.strcat(self.b_ch, self.u_ch), target)
        self.assertEqual(functool.strcat(self.u_ch, self.b_ch), target)

        gbk_ch = u"测试".encode("gbk")
        self.assertEqual(
            functool.strcat(gbk_ch, self.b_ch, "gbk", "utf-8"), target)
        self.assertEqual(
            functool.strcat(gbk_ch, self.u_ch, "gbk", "utf-8"), target)
        self.assertEqual(
            functool.strcat(self.b_ch, gbk_ch, "utf-8", "gbk"), target)
        self.assertEqual(
            functool.strcat(self.u_ch, gbk_ch, "utf-8", "gbk"), target)
