from file_management.filemanager import *
from const import const
from file_management.replacemanager import *
import numpy as np

sys.path.append("../")


class BufPageManager:
    def __init__(self):
        self.file_manager = FileManager()
        self.replace_manager = ReplaceManager(const.PAGE_NUM_CAP-1)
        self.data = [None]*const.PAGE_NUM_CAP
        self.dirty = [0]*const.PAGE_NUM_CAP
        # file_id page_id to index
        self.query = dict()
        # index to file_id page_id
        self.anti_query = dict()
        self.open_file_to_id = dict()
        self.open_id_to_file = dict()

    def create_file(self, filename):
        self.file_manager.create_file(filename)

    def open_file(self, filename):
        if filename in self.open_file_to_id:
            return self.open_file_to_id.get(filename)
        file_id = self.file_manager.open_file(filename)
        self.open_file_to_id[filename] = file_id
        self.open_id_to_file[file_id] = filename
        return file_id

    def remove_file(self,filename):
        self.remove_file(filename)

    def write_back(self, index):
        if self.data[index] is None:
            return
        file_id, page_id = self.anti_query.get(index)
        if self.dirty[index] == 1:
            write_page(file_id, page_id, self.data[index])
            self.dirty[index] = 0
        self.anti_query.pop(index)
        self.query.pop((file_id, page_id))
        self.data[index] = None

    def close_file(self, filename):
        for index in range(0, const.PAGE_NUM_CAP):
            self.write_back(index)
        file_id = self.open_file_to_id[filename]
        self.open_file_to_id.pop(filename)
        self.open_id_to_file.pop(file_id)
        close_file(file_id)

    def close(self):
        for index in range(0, const.PAGE_NUM_CAP):
            self.write_back(index)

    def read_page(self, file_id, page_id) -> bytes:
        if (file_id, page_id) in self.query.keys():
            index = self.query.get((file_id, page_id))
            data = self.data[index]
            self.replace_manager.access(index)
            return data
        index = self.replace_manager.find()
        if self.data[index] is not None:
            self.write_back(index)
        self.query[(file_id, page_id)] = index
        self.anti_query[index] = (file_id, page_id)
        data = read_page(file_id, page_id)
        self.data[index] = data
        return data

    def write_page(self, file_id, page_id, write_data: bytes):
        if (file_id, page_id) in self.query.keys():
            index = self.query.get((file_id, page_id))
            self.data[index] = write_data
            self.dirty[index] = 1
        else:
            write_page(file_id, page_id, write_data)    # TODO:change it into cache

    def write_page_sudo(self, file_id, page_id, write_data: bytes):
        write_page(file_id, page_id, write_data)







