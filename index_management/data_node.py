from record_management import RID
from const import const
from exception import exception


class DataNode:
    def __init__(self, parent):
        self.data = []
        self.parent = parent
        self.type = 1

    def insert(self, key: int, rid: RID):
        insert = False
        for i in range(0, len(self.data)):
            if key == self.data[i].key:
                raise exception.SameKeyError
            if key > self.data[i].key:
                continue
            self.data.insert(i, {key: id})
            insert = True
        if not insert:
            self.data.insert(len(self.data), {key: rid})
        if len(self.data) > const.B_TREE_LEAF:
            return {"data": self.split()}
        return {"lower_bound:": self.data[0].key, "upper_bound": self.data[-1].key}

    def split(self):
        return self.data[:len(self.data) // 2], self.data[len(self.data) // 2:]

    def delete(self, rid: RID):
        if rid in self.data:
            self.data.remove(rid)
        if len(self.data) == 0:
            return False
        return True

    def change_parent(self, parent):
        self.parent = parent

    def search(self, lower_bound, upper_bound):
        lower_bound_index = self.bisect_left(self.data, lower_bound, 0, len(self.data), key=lambda x: x.key)
        upper_bound_index = self.bisect_right(self.data, upper_bound, 0, len(self.data), key=lambda x: x.key)
        return self.data[lower_bound_index: upper_bound_index]

    @staticmethod
    def bisect_right(a, x, lo=0, hi=None, *, key=None):
        if lo < 0:
            raise ValueError('lo must be non-negative')
        if hi is None:
            hi = len(a)
        # Note, the comparison uses "<" to match the
        # __lt__() logic in list.sort() and in heapq.
        if key is None:
            while lo < hi:
                mid = (lo + hi) // 2
                if x < a[mid]:
                    hi = mid
                else:
                    lo = mid + 1
        else:
            while lo < hi:
                mid = (lo + hi) // 2
                if x < key(a[mid]):
                    hi = mid
                else:
                    lo = mid + 1
        return lo

    @staticmethod
    def bisect_left(a, x, lo=0, hi=None, *, key=None):
        if lo < 0:
            raise ValueError('lo must be non-negative')
        if hi is None:
            hi = len(a)
        # Note, the comparison uses "<" to match the
        # __lt__() logic in list.sort() and in heapq.
        if key is None:
            while lo < hi:
                mid = (lo + hi) // 2
                if a[mid] < x:
                    lo = mid + 1
                else:
                    hi = mid
        else:
            while lo < hi:
                mid = (lo + hi) // 2
                if key(a[mid]) < x:
                    lo = mid + 1
                else:
                    hi = mid
        return lo



