from unittest import TestCase
from operator import attrgetter

from ycyc.libs.algorithms.sequences import alignment


class TestAlignment(TestCase):
    def test_usage(self):
        a = list(range(20))
        b = a[::2]
        c = a[::3]

        alignment_seq = alignment.alignment_seq([a, b, c])
        self.assertListEqual(next(alignment_seq), [0, 0, 0])
        self.assertListEqual(next(alignment_seq), [6, 6, 6])
        self.assertListEqual(next(alignment_seq), [12, 12, 12])
        self.assertListEqual(next(alignment_seq), [18, 18, 18])

        alignment_seq = alignment.alignment_seq(
            [a, b, c], key_func=attrgetter("real"),
        )
        self.assertListEqual(next(alignment_seq), [0, 0, 0])
        self.assertListEqual(next(alignment_seq), [6, 6, 6])
        self.assertListEqual(next(alignment_seq), [12, 12, 12])
        self.assertListEqual(next(alignment_seq), [18, 18, 18])
