class LinkList:
    class Node:
        def __init__(self, _prev, _next):
            self._prev = _prev
            self._next = _next

        @property
        def prev(self):
            return self._prev

        @prev.setter
        def prev(self, value):
            self._prev = value

        @property
        def next(self):
            return self._next

        @next.setter
        def next(self, value):
            self._next = value

    def __init__(self, cap, list_num):
        self._cap = cap
        self._list_num = list_num
        self._list = list()
        for i in range(0, cap + list_num):
            self._list.append(self.Node(i, i))

    def link(self, _prev: int, _next: int):
        self._list[_next].prev = _prev
        self._list[_prev].next = _next

    def delete(self, index: int):
        if self._list[index].prev is index:
            return
        self.link(self._list[index].prev, self._list[index].next)
        self._list[index].prev = index
        self._list[index].next = index

    def insert(self, list_id, ele):
        self.delete(ele)
        node = list_id + ele
        prev = self._list[node].prev
        self.link(prev, ele)
        self.link(ele, node)

    def insert_first(self, list_id, ele):
        self.delete(ele)
        node = list_id + ele
        _next = self._list[node].next
        self.link(node, ele)
        self.link(ele, _next)

    def get_first(self, list_id):
        return self._list[list_id + self._cap].next

    def next(self, index):
        return self._list[index].next

    def is_head(self, index):
        if index < self._cap:
            return False
        return True

    def is_alone(self, index):
        return self._list[index].next is index
