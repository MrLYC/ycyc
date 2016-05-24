from threading import RLock
import heapq as heapq_op

from ycyc.base.iterutils import getattrs


class HeapIsEmpty(Exception):
    pass


class HeapItem(object):

    def __init__(self, value, heap):
        self.value = value
        self.heap = heap

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "%s(%r, %r)" % (
            self.__class__.__name__, self.value, self.heap,
        )

    def __cmp__(self, other):
        return self.heap.compare_items(self, other)


class Heap(object):

    def __init__(self, iterable=(), cmp_attrs=(), reverse=False):
        self.data = list(
            HeapItem(i, self)
            for i in iterable
        )
        self.cmp_attrs = cmp_attrs
        self.reverse = reverse
        heapq_op.heapify(self.data)

    def compare_items(self, item1, item2):
        value = cmp(
            getattrs(item1.value, self.cmp_attrs),
            getattrs(item2.value, self.cmp_attrs),
        )
        return value * -1 if self.reverse else value

    def __getitem__(self, index):
        item = self.data[index]
        return item.value

    def __iter__(self):
        return iter(self.headn(len(self.data)))

    def push(self, value):
        item = HeapItem(value, self)
        heapq_op.heappush(self.data, item)

    def pop(self):
        if not self.data:
            raise HeapIsEmpty()
        item = heapq_op.heappop(self.data)
        return item.value

    def edge_out(self, value):
        item = heapq_op.heapreplace(self.data, HeapItem(value, self))
        return item.value

    def headn(self, n):
        return [
            i.value for i in heapq_op.nsmallest(n, self.data)
        ]

    def tailn(self, n):
        values = [
            i.value for i in heapq_op.nlargest(n, self.data)
        ]
        return values[::-1]


class ThreadSafetyHeap(Heap):
    def __init__(self, *args, **kwargs):
        super(ThreadSafetyHeap, self).__init__(*args, **kwargs)
        self.siftup_lock = RLock()

    def push(self, *args, **kwargs):
        with self.siftup_lock:
            return super(ThreadSafetyHeap, self).push(*args, **kwargs)

    def pop(self, *args, **kwargs):
        with self.siftup_lock:
            return super(ThreadSafetyHeap, self).pop(*args, **kwargs)

    def edge_out(self, *args, **kwargs):
        with self.siftup_lock:
            return super(ThreadSafetyHeap, self).edge_out(*args, **kwargs)
