import heapq


class SeqHeapItem(object):

    def __init__(self, sequence, cmp_func):
        self.sequence = iter(sequence)
        self.cmp_func = cmp_func
        self.value = None
        self.backward()

    def backward(self):
        self.value = next(self.sequence)

    def __cmp__(self, other):
        return self.cmp_func(self.value, other.value)


def alignment_seq(sequences, key_func=None, cmp_func=None):
    key_func = key_func or (lambda x: x)
    cmp_func = cmp_func or (lambda x, y: cmp(key_func(x), key_func(y)))

    seq_heap = [SeqHeapItem(i, cmp_func) for i in sequences]

    while seq_heap:
        try:
            heapq.heapify(seq_heap)
            min_item = heapq.nsmallest(1, seq_heap)[0]
            max_item = heapq.nlargest(1, seq_heap)[0]

            if min_item == max_item:
                yield [i.value for i in seq_heap]
                backward_seq = seq_heap
            else:
                backward_seq = (i for i in seq_heap if i < max_item)

            for i in backward_seq:
                i.backward()

        except StopIteration:
            break
