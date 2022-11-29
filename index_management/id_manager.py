from .tree import Node
from .index import Index
from const import const
from record_management import RID
import os


class IdManager:
    def __init__(self):
        self.index_list = {}

    @staticmethod
    def create_index(index_name, current_path):
        index = Index(index_name)
        index.dump(current_path + '/' + index_name + const.INDEX_FILE)

    def destroy_index(self, index, current_path):
        os.remove(path=current_path + '/' + index + const.INDEX_FILE)
        if index in self.index_list.keys():
            self.index_list.pop(index)

    def read_index(self, index_name, current_path):
        index = Index(index_name, False, current_path + '/' + index_name + const.INDEX_FILE)
        self.index_list[index_name] = index

    def close(self, current_path):
        for index in self.index_list.keys():
            self.index_list[index].dump(current_path + '/' + index + const.INDEX_FILE)

    def insert_rec(self, index, key, rid: RID):
        index = self.index_list[index]
        index.insert(key, rid)

    def delete_rec(self, index, key):
        index = self.index_list[index]
        index.delete(key)

    def search(self, index, lower_bound, upper_bound):
        index = self.index_list[index.index_name]
        result = index.search(lower_bound, upper_bound)
        return result

    def search_both(self, index, lower_bound, upper_bound):
        index = self.index_list[index.index_name]
        return index.search_both(lower_bound, upper_bound)
