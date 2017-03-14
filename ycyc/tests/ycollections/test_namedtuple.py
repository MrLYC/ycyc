# encoding: utf-8

from unittest import TestCase

from ycyc.ycollections import namedtuple


class TestNamedTuple(TestCase):
    def test_usage(self):
        person = namedtuple.namedtuple(
            "Person", ["name", "sex"],
        )
        bill = person("Bill", sex="m")
        self.assertEqual(bill.name, "Bill")
        self.assertEqual(bill.sex, "m")
        self.assertEqual(bill[0], "Bill")
        self.assertEqual(bill[1], "m")

        person = namedtuple.namedtuple(
            "Person", ["name", "sex"], {"id": None},
        )
        bill = person("Bill", sex="m")
        self.assertEqual(bill.name, "Bill")
        self.assertEqual(bill.sex, "m")
        self.assertEqual(bill.id, None)
        self.assertEqual(bill[0], "Bill")
        self.assertEqual(bill[1], "m")
        self.assertEqual(bill[2], None)

        bill = person("Bill", sex="m", id=1)
        self.assertEqual(bill.id, 1)
        bill = person("Bill", "m", 2)
        self.assertEqual(bill.id, 2)

        with self.assertRaises(AttributeError):
            bill.id = 3
