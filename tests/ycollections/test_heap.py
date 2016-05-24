from unittest import TestCase

from ycyc.ycollections.heap import Heap, HeapIsEmpty


class TestHeap(TestCase):
    class PriorityTask(object):
        def __init__(self, priority, value):
            self.priority = priority
            self.value = value

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

    def test_push(self):
        heap = Heap()
        heap.push(3)
        self.assertListEqual(list(heap), [3])
        heap.push(1)
        self.assertListEqual(list(heap), [1, 3])
        heap.push(2)
        self.assertListEqual(list(heap), [1, 2, 3])

    def test_pop(self):
        heap = Heap([3, 2, 1])
        self.assertListEqual(list(heap), [1, 2, 3])
        heap.pop()
        self.assertListEqual(list(heap), [2, 3])
        heap.pop()
        self.assertListEqual(list(heap), [3])
        heap.pop()
        self.assertListEqual(list(heap), [])
        with self.assertRaises(HeapIsEmpty):
            heap.pop()

    def test_headn(self):
        heap = Heap([3, 1, 17, 25, 19])
        self.assertListEqual(
            heap.headn(3),
            [1, 3, 17]
        )
        heap = Heap([3, 1, 17, 25, 19], reverse=True)
        self.assertListEqual(
            heap.headn(3),
            [25, 19, 17]
        )

    def test_tailn(self):
        heap = Heap([3, 1, 17, 25, 19])
        self.assertListEqual(
            heap.tailn(3),
            [17, 19, 25]
        )

        heap = Heap([3, 1, 17, 25, 19], reverse=True)
        self.assertListEqual(
            heap.tailn(3),
            [17, 3, 1]
        )

    def test_edge_out(self):
        heap = Heap([3, 1, 2])
        self.assertEqual(1, heap.edge_out(4))
        self.assertEqual(2, heap.edge_out(5))
        self.assertEqual(3, heap.edge_out(6))
        self.assertEqual(4, heap.edge_out(7))

    def test_cmp_attrs(self):
        heap = Heap(cmp_attrs=["priority"])
        heap.push(self.PriorityTask(5, 0))
        heap.push(self.PriorityTask(8, 1))
        heap.push(self.PriorityTask(3, 2))
        heap.push(self.PriorityTask(4, 3))
        heap.push(self.PriorityTask(9, 4))
        self.assertListEqual(
            [i.value for i in heap],
            [2, 3, 0, 1, 4]
        )

        heap = Heap(cmp_attrs=["priority"], reverse=True)
        heap.push(self.PriorityTask(5, 0))
        heap.push(self.PriorityTask(8, 1))
        heap.push(self.PriorityTask(3, 2))
        heap.push(self.PriorityTask(4, 3))
        heap.push(self.PriorityTask(9, 4))
        self.assertListEqual(
            [i.value for i in heap],
            [4, 1, 0, 3, 2]
        )
