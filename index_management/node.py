class Node(object):
    """Base node object.
    Each node stores keys and values. Keys are not unique to each value, and as such values are
    stored as a list under each key.
    Attributes:
        order (int): The maximum number of keys each node can hold.
    """
    def __init__(self, order):
        """Child nodes can be converted into parent nodes by setting self.leaf = False. Parent nodes
        simply act as a medium to traverse the tree."""
        self.order = order
        self.keys = []
        self.values = []
        self.leaf = True

    def add(self, key, value):
        """Adds a key-value pair to the node."""
        # If the node is empty, simply insert the key-value pair.
        if not self.keys:
            self.keys.append(key)
            self.values.append([value])
            return None

        for i, item in enumerate(self.keys):
            # If new key matches existing key, add to list of values.
            if key == item:
                self.values[i].append(value)
                break

            # If new key is smaller than existing key, insert new key to the left of existing key.
            elif key < item:
                self.keys = self.keys[:i] + [key] + self.keys[i:]
                self.values = self.values[:i] + [[value]] + self.values[i:]
                break

            # If new key is larger than all existing keys, insert new key to the right of all
            # existing keys.
            elif i + 1 == len(self.keys):
                self.keys.append(key)
                self.values.append([value])
                break

    def split(self):
        """Splits the node into two and stores them as child nodes."""
        left = Node(self.order)
        right = Node(self.order)
        mid = self.order // 2

        left.keys = self.keys[:mid]
        left.values = self.values[:mid]

        right.keys = self.keys[mid:]
        right.values = self.values[mid:]

        # When the node is split, set the parent key to the left-most key of the right child node.
        self.keys = [right.keys[0]]
        self.values = [left, right]
        self.leaf = False

    def is_full(self):
        """Returns True if the node is full."""
        return len(self.keys) == self.order

    def show(self, counter=0):
        """Prints the keys at each level."""
        print(counter, str(self.keys), self.leaf)

        # Recursively print the key of child nodes (if these exist).
        if not self.leaf:
            for item in self.values:
                item.show(counter + 1)

    def delete(self, key):
        if self.leaf:
            for i, item in enumerate(self.keys):
                if key == item:
                    self.keys.pop(i)
                    self.values.pop(i)
                    if len(self.keys) == 0:
                        return True
                    return False
            return False
        else:
            for i, item in enumerate(self.keys):
                if key < item:
                    return self.values[i].delete(key)
                elif i + 1 == len(self.keys):
                    return self.values[i+1].delete(key)

    def search(self, lower_bound, upper_bound):
        if self.leaf:
            lower_bound_index = self.bisect_left(self.keys, lower_bound, 0, len(self.keys))
            upper_bound_index = self.bisect_right(self.keys, upper_bound, 0, len(self.keys))
            keys = []
            values = []
            for i in range(lower_bound_index, upper_bound_index):
                keys.append(self.keys[i])
                values.extend(self.values[i])
            return keys, values
        else:
            ret_keys = []
            ret_values = []
            lower_bound_index = self.bisect_left(self.keys, lower_bound, 0, len(self.keys))
            upper_bound_index = self.bisect_right(self.keys, upper_bound, 0, len(self.keys))
            for i in range(lower_bound_index, max(len(self.keys) + 1, upper_bound_index + 1)):
                key, value = self.values[i].search(lower_bound, upper_bound)
                ret_keys.extend(key)
                ret_values.extend(value)
            return ret_keys, ret_values

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

    def dump(self, clock, dic: dict):
        if clock in dic:
            print("error!")
            exit(-1)
        if self.leaf:
            dic[clock] = {"order": self.order, "keys": self.keys,
                          "values": [[each.to_string() for each in value] for value in self.values], "leaf": self.leaf}
            return clock, dic
        else:
            child = []
            my_clock = clock
            for i in self.values:
                child.append(my_clock + 1)
                my_clock, dic = i.dump(my_clock+1, dic)
            dic[clock] = {"order": self.order, "keys": self.keys, "values": child, "leaf": self.leaf}
            return my_clock, dic

    def check_single(self):
        if self.leaf:
            for value in self.values:
                if len(value) > 1:
                    return False
            return True
        else:
            for child in self.values:
                if not child.check_single():
                    return False
            return True



