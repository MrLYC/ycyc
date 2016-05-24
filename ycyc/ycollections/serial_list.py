from ycyc.ycollections.heap import Heap


class SerialListItem(object):
    def __init__(self, sn, value):
        self.sn = sn
        self.value = value


class SerialList(object):
    def __init__(self, sn=0, reverse=False):
        self.next_sn = sn
        self.heap = Heap(cmp_attrs=["sn"], reverse=False)

    def push_item(self, item):
        self.heap.push(item)

    def push(self, sn, value):
        self.push_item(SerialListItem(sn, value))

    def pop_item(self, force=False):
        while True:
            items = self.heap.headn(1)
            if not items:
                break
            item = items[0]

            if item.sn < self.next_sn:
                self.heap.pop()
            elif item.sn == self.next_sn or force:
                item = self.heap.pop()
                self.next_sn = item.sn + 1
                return item
            else:
                break
        return None

    def pop(self, force=False):
        item = self.pop_item(force)
        return item and item.value
