import sys
from .linklist import LinkList

sys.path.append("../")


class ReplaceManager:
    def __init__(self, cap):
        self.cap = cap
        self._list = LinkList(cap, 1)
        for i in range(0, cap):
            self._list.insert(0, i)

    def free(self, index):
        self._list.insert_first(0, index)

    def access(self, index):
        self._list.insert(0, index)

    def find(self):
        index = self._list.get_first(0)
        self._list.delete(index)
        self._list.insert(0, index)
        return index
