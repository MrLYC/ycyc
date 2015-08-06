#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase

from ycyc.base import txtutils


class TestCoding(TestCase):
    b_en = b"test"
    b_ch = u"测试".encode("utf-8")
    u_en = u"test"
    u_ch = u"测试"

    def test_encode(self):
        self.assertEqual(self.b_en, txtutils.encode(self.u_en, "utf-8"))
        self.assertEqual(self.b_ch, txtutils.encode(self.u_ch, "utf-8"))
        self.assertEqual(self.b_en, txtutils.encode(self.b_en, "utf-8"))
        self.assertEqual(self.b_ch, txtutils.encode(self.b_ch, "utf-8"))

    def test_decode(self):
        self.assertEqual(self.u_en, txtutils.decode(self.u_en, "utf-8"))
        self.assertEqual(self.u_ch, txtutils.decode(self.u_ch, "utf-8"))
        self.assertEqual(self.u_en, txtutils.decode(self.b_en, "utf-8"))
        self.assertEqual(self.u_ch, txtutils.decode(self.b_ch, "utf-8"))

    def test_bytescat(self):
        target = u"test测试".encode("utf-8")
        self.assertEqual(txtutils.bytescat(self.b_en, self.b_ch), target)
        self.assertEqual(txtutils.bytescat(self.u_en, self.u_ch), target)
        self.assertEqual(txtutils.bytescat(self.b_en, self.u_ch), target)
        self.assertEqual(txtutils.bytescat(self.u_en, self.b_ch), target)

        target = u"测试测试".encode("utf-8")
        self.assertEqual(txtutils.bytescat(self.b_ch, self.b_ch), target)
        self.assertEqual(txtutils.bytescat(self.u_ch, self.u_ch), target)
        self.assertEqual(txtutils.bytescat(self.b_ch, self.u_ch), target)
        self.assertEqual(txtutils.bytescat(self.u_ch, self.b_ch), target)

    def test_strcat(self):
        target = u"test测试"
        self.assertEqual(txtutils.strcat(self.b_en, self.b_ch), target)
        self.assertEqual(txtutils.strcat(self.u_en, self.u_ch), target)
        self.assertEqual(txtutils.strcat(self.b_en, self.u_ch), target)
        self.assertEqual(txtutils.strcat(self.u_en, self.b_ch), target)

        target = u"测试测试"
        self.assertEqual(txtutils.strcat(self.b_ch, self.b_ch), target)
        self.assertEqual(txtutils.strcat(self.u_ch, self.u_ch), target)
        self.assertEqual(txtutils.strcat(self.b_ch, self.u_ch), target)
        self.assertEqual(txtutils.strcat(self.u_ch, self.b_ch), target)

        gbk_ch = u"测试".encode("gbk")
        self.assertEqual(
            txtutils.strcat(gbk_ch, self.b_ch, "gbk", "utf-8"), target)
        self.assertEqual(
            txtutils.strcat(gbk_ch, self.u_ch, "gbk", "utf-8"), target)
        self.assertEqual(
            txtutils.strcat(self.b_ch, gbk_ch, "utf-8", "gbk"), target)
        self.assertEqual(
            txtutils.strcat(self.u_ch, gbk_ch, "utf-8", "gbk"), target)


class TestStringUtils(TestCase):
    def test_drop_prefix(self):
        self.assertEqual(
            txtutils.drop_prefix("root/file.txt", "root/"),
            "file.txt"
        )
        self.assertEqual(
            txtutils.drop_prefix("dir/file.txt", "root/"),
            "dir/file.txt"
        )

    def test_drop_postfix(self):
        self.assertEqual(
            txtutils.drop_postfix("file.txt", ".txt"),
            "file"
        )
        self.assertEqual(
            txtutils.drop_postfix("file.tmp", ".txt"),
            "file.tmp"
        )

    def test_split_and_strip(self):
        self.assertListEqual(
            txtutils.split_and_strip("a,b ,c, d , e"),
            ["a", "b", "c", "d", "e"]
        )

    def test_left_part_of(self):
        txt = "xxx.avi.part1.rar"
        self.assertEqual(txtutils.left_part_of(txt, "."), "xxx")
        self.assertEqual(txtutils.left_part_of(txt, ".", 0), "")
        self.assertEqual(txtutils.left_part_of(txt, ".", 1), "xxx")
        self.assertEqual(txtutils.left_part_of(txt, ".", 2), "xxx.avi")
        self.assertEqual(txtutils.left_part_of(txt, ".", -1), "xxx.avi.part1")
        self.assertEqual(txtutils.left_part_of(txt, ".", -2), "xxx.avi")

    def test_right_part_of(self):
        txt = "xxx.avi.part1.rar"
        self.assertEqual(txtutils.right_part_of(txt, "."), "rar")
        self.assertEqual(txtutils.right_part_of(txt, ".", 0), txt)
        self.assertEqual(txtutils.right_part_of(txt, ".", -1), "rar")
        self.assertEqual(txtutils.right_part_of(txt, ".", -2), "part1.rar")
        self.assertEqual(txtutils.right_part_of(txt, ".", 1), "avi.part1.rar")
        self.assertEqual(txtutils.right_part_of(txt, ".", 2), "part1.rar")


class TestTxtDistance(TestCase):
    def test_edit_distance(self):
        test_cases = {
            ("ABC", "CBCD"): 2,
            ("FOOD", "MONEY"): 4,
            ("ISLANDER", "SLANDER"): 1,
            ("MART", "KARMA"): 3,
            ("SITTING", "SITTING"): 0,
            ("INTENTION", "EXECUTION"): 5,
            ("", "AA"): 2,
            ("B", ""): 1,
        }
        edit_distance = txtutils.TxtDistance.edit_distance
        edit_distance2 = txtutils.TxtDistance.edit_distance2

        for case, result in test_cases.items():
            s1, s2 = case
            self.assertEqual(edit_distance(s1, s2), result)
            self.assertEqual(edit_distance2(s1, s2), result)

    def test_hamming_distance(self):
        test_cases = {
            ("12345", "54321"): 4,
            ("karolin", "kathrin"): 3,
            ("karolin", "kerstin"): 3,
            ("1011101", "1001001 "): 2,
            ("2173896", "2233796"): 3,
        }

        for case, result in test_cases.items():
            s1, s2 = case
            self.assertEqual(
                txtutils.TxtDistance.hamming_distance(s1, s2),
                result,
            )


class TestSepJoin(TestCase):
    def test_usage(self):
        self.assertEqual(
            txtutils.sep_join("|", map(str, range(3))),
            "0|1|2"
        )
        self.assertEqual(
            txtutils.sep_join("|", map(str, range(3)), True),
            "|0|1|2"
        )
        self.assertEqual(
            txtutils.sep_join("|", map(str, range(3)), True, True),
            "|0|1|2|"
        )
        self.assertEqual(
            txtutils.sep_join(" | ", map(str, range(3)), "| ", " |"),
            "| 0 | 1 | 2 |"
        )
        self.assertEqual(
            txtutils.sep_join(",", map(str, range(3)), "x="),
            "x=0,1,2"
        )
