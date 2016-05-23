from unittest import TestCase

from ycyc.ycollections.heap import Heap


class TestHeap(TestCase):

    def test_construction(self):
        Heap()
        Heap([2, 3, 1, 17, 19, 100, 25, 17, 36])
        Heap(range(10), cmp_attrs=["real"])
        Heap(range(10), reverse=True)

    def test_iter(self):
        heap = Heap([2, 3, 1, 17, 19, 100, 25, 17, 36])
        self.assertListEqual(
            list(heap),
            [1, 2, 3, 17, 17, 19, 25, 36, 100]
        )

        heap = Heap([2, 3, 1, 17, 19, 100, 25, 17, 36], reverse=True)
        self.assertListEqual(
            list(heap),
            [100, 36, 25, 19, 17, 17, 3, 2, 1]
        )

        heap = Heap([2, 3, 1, 17, 19, 100, 25, 17, 36], cmp_attrs=["real"])
        self.assertListEqual(
            list(heap),
            [1, 2, 3, 17, 17, 19, 25, 36, 100]
        )

    def test_push_and_pop(self):
        heap = Heap()
        heap.push(3)
        heap.push(1)
        heap.push(2)
        self.assertListEqual(list(heap), [1, 2, 3])
        self.assertEqual(heap.pop(), 1)
        self.assertListEqual(list(heap), [2, 3])

    def test_topn(self):
        heap = Heap([3, 1, 17, 25, 19])
        self.assertListEqual(
            heap.topn(3),
            [1, 3, 17]
        )
        heap = Heap([3, 1, 17, 25, 19], reverse=True)
        self.assertListEqual(
            heap.topn(3),
            [25, 19, 17]
        )

    def test_lastn(self):
        heap = Heap([3, 1, 17, 25, 19])
        self.assertListEqual(
            heap.lastn(3),
            [25, 19, 17]
        )

        heap = Heap([3, 1, 17, 25, 19], reverse=True)
        self.assertListEqual(
            heap.lastn(3),
            [1, 3, 17]
        )
