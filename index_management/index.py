from .tree import BPlusTree
from .node import Node
import json
from record_management import RID
from const import const


class Index:
    def __init__(self, index_name, empty=True, save_path=None):
        # self.db_name = db_name
        # self.file_id = file_id
        self.index_name = index_name
        if empty:
            self.tree = BPlusTree(const.B_TREE_LEAF)
        else:
            self.tree = self.load(save_path=save_path)

    def dump(self, save_path):
        _, dic = self.tree.dump()
        with open(save_path, 'w') as f:
            f.write(json.dumps(dic))
            f.close()

    def load(self, save_path):
        with open(save_path, 'r') as f:
            dic = json.loads(f.read())
            f.close()
        root = self.create_node(0, dic)
        return BPlusTree(order=root.order, root=root)

    def create_node(self, index, dic):
        info = dic[str(index)]
        if info['leaf']:
            node = Node(info['order'])
            node.keys = info['keys']
            node.values = [[RID(int(each.split('_')[0]), int(each.split('_')[1])) for each in value]
                           for value in info['values']]
            node.leaf = info['leaf']
            return node
        else:
            node = Node(info['order'])
            node.keys = info['keys']
            for i in info['values']:
                child = self.create_node(i, dic)
                node.values.append(child)
            node.leaf = info['leaf']
            return node

    def insert(self, key, value: RID):
        self.tree.insert(key, value)
        # print(self.tree.show())

    def delete(self, key):
        self.tree.delete(key)

    def search(self, lower_bound, upper_bound):
        return self.tree.search(lower_bound, upper_bound)

    def search_both(self, lower_bound, upper_bound):
        return self.tree.search_both(lower_bound, upper_bound)

    def check_single(self):
        return self.tree.check_single()
