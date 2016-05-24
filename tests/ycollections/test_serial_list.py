from unittest import TestCase

from ycyc.ycollections.serial_list import SerialList


class TestSerialList(TestCase):
    def test_usage(self):
        serial_list = SerialList()
        self.assertEqual(0, serial_list.next_sn)
        serial_list.push(1, 1)
        serial_list.push(0, 2)
        serial_list.push(3, 3)

        item = serial_list.pop_item()
        self.assertEqual(0, item.sn)
        self.assertEqual(2, item.value)
        self.assertEqual(1, serial_list.next_sn)

        item = serial_list.pop_item()
        self.assertEqual(1, item.sn)
        self.assertEqual(1, item.value)
        self.assertEqual(2, serial_list.next_sn)

        item = serial_list.pop_item()
        self.assertIsNone(item)
        self.assertEqual(2, serial_list.next_sn)

        item = serial_list.pop_item(force=True)
        self.assertEqual(3, item.sn)
        self.assertEqual(3, item.value)
        self.assertEqual(4, serial_list.next_sn)

        serial_list.push(2, 4)
        item = serial_list.pop_item()
        self.assertIsNone(item)
        self.assertEqual(4, serial_list.next_sn)

        serial_list.push(4, 5)
        item = serial_list.pop_item()
        self.assertEqual(4, item.sn)
        self.assertEqual(5, item.value)
        self.assertEqual(5, serial_list.next_sn)
