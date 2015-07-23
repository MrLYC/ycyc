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


class TestStringUtils(TestCase):
    def test_drop_prefix(self):
        self.assertEqual(
            funcutils.drop_prefix("root/file.txt", "root/"),
            "file.txt"
        )
        self.assertEqual(
            funcutils.drop_prefix("dir/file.txt", "root/"),
            "dir/file.txt"
        )

    def test_drop_postfix(self):
        self.assertEqual(
            funcutils.drop_postfix("file.txt", ".txt"),
            "file"
        )
        self.assertEqual(
            funcutils.drop_postfix("file.tmp", ".txt"),
            "file.tmp"
        )

    def test_split_and_strip(self):
        self.assertListEqual(
            funcutils.split_and_strip("a,b ,c, d , e"),
            ["a", "b", "c", "d", "e"]
        )

    def test_left_part_of(self):
        txt = "xxx.avi.part1.rar"
        self.assertEqual(funcutils.left_part_of(txt, "."), "xxx")
        self.assertEqual(funcutils.left_part_of(txt, ".", 0), "")
        self.assertEqual(funcutils.left_part_of(txt, ".", 1), "xxx")
        self.assertEqual(funcutils.left_part_of(txt, ".", 2), "xxx.avi")
        self.assertEqual(funcutils.left_part_of(txt, ".", -1), "xxx.avi.part1")
        self.assertEqual(funcutils.left_part_of(txt, ".", -2), "xxx.avi")

    def test_right_part_of(self):
        txt = "xxx.avi.part1.rar"
        self.assertEqual(funcutils.right_part_of(txt, "."), "rar")
        self.assertEqual(funcutils.right_part_of(txt, ".", 0), txt)
        self.assertEqual(funcutils.right_part_of(txt, ".", -1), "rar")
        self.assertEqual(funcutils.right_part_of(txt, ".", -2), "part1.rar")
        self.assertEqual(funcutils.right_part_of(txt, ".", 1), "avi.part1.rar")
        self.assertEqual(funcutils.right_part_of(txt, ".", 2), "part1.rar")


class TestObjectHelper(TestCase):
    def test_is_magic_method(self):
        class Foo(object):
            def __str__(self):
                return "foo"

        foo = Foo()
        self.assertTrue(funcutils.is_magic_method(Foo.__str__))
        self.assertTrue(funcutils.is_magic_method(foo.__str__))

    def test_set_default_attr(self):
        class Foo(object):
            def __str__(self):
                return "foo"

        foo = Foo()
        self.assertFalse(hasattr(foo, "foobarbaz"))
        self.assertTrue(funcutils.set_default_attr(
            foo, "foobarbaz", True
        ))
        self.assertTrue(foo.foobarbaz)
        self.assertTrue(funcutils.set_default_attr(
            foo, "foobarbaz", False
        ))
        self.assertTrue(foo.foobarbaz)

    def test_iter_attrs(self):
        class Foo(object):
            Public = 0
            _Protected = 1
            __Privated = 2

            def __init__(self):
                self.public = 4
                self._protected = 5
                self.__privated = 6

            def get_privated(self):
                return self.__privated

            @property
            def protected(self):
                return self._protected

        foo = Foo()

        self.assertDictEqual(
            dict(funcutils.iter_attrs(foo)),
            {
                "Public": 0, "public": 4, "protected": 5,
            }
        )
        self.assertDictEqual(
            dict(funcutils.iter_attrs(foo, public_only=False)),
            {
                "Public": 0, "_Protected": 1, "public": 4,
                "protected": 5, "_protected": 5,
            }
        )
        self.assertDictEqual(
            dict(funcutils.iter_attrs(foo, include_fields={"_Protected"})),
            {
                "Public": 0, "_Protected": 1, "public": 4,
                "protected": 5,
            }
        )
        self.assertDictEqual(
            dict(funcutils.iter_attrs(foo, exclude_fields={"protected"})),
            {
                "Public": 0, "public": 4,
            }
        )
        result = dict(funcutils.iter_attrs(foo, exclude_methods=False))
        self.assertEqual(result["get_privated"], foo.get_privated)

        self.assertIn(
            "_Protected",
            dict(funcutils.iter_attrs(
                foo,
                include_fields={"_Protected"},
                exclude_fields={"_Protected"}
            ))
        )


class TestFilterN(TestCase):
    def test_filter_n(self):
        self.assertListEqual(
            [1, 3],
            funcutils.filter_n(lambda x: x % 2, range(10), 2)
        )
        self.assertListEqual(
            [1],
            funcutils.filter_n(None, range(10), 1)
        )

