from .rid import RID
from file_management.bufpagemanager import BufPageManager
from .rc_handler import RCHandler
import json
import numpy as np


class RCManager:
    def __init__(self):
        self.file_manager = BufPageManager()
        self.handle_helper = dict()

    def close(self):
        for handle in self.handle_helper.values():
            self.file_manager.write_page_sudo(handle.file_id, 0, json.dumps(handle.close()).encode('utf-8'))
        self.file_manager.close()

    def create_file(self, filename, slot_size):
        self.file_manager.create_file(filename)
        file_id = self.file_manager.open_file(filename)
        info = {'page_num': 2, 'valid_page': 1, 'slot_size': slot_size}
        self.file_manager.write_page(file_id, 0, json.dumps(info).encode('utf-8'))
        default = np.zeros(256).tobytes()
        self.file_manager.write_page(file_id, 1, default)
        self.close_file(filename)

    def close_file(self, filename):
        self.file_manager.close_file(filename)
        if filename in self.handle_helper.keys():
            self.handle_helper.pop(filename)

    def open_file(self, filename):
        file_id = self.file_manager.open_file(filename)
        rc_handle = RCHandler(file_id, self.file_manager)
        self.handle_helper[filename] = rc_handle

    def destroy_file(self,  filename):
        self.close_file(filename)
        self.file_manager.remove_file(filename)

    def insert_data(self, filename, data: np.ndarray):
        if filename not in self.handle_helper.keys():
            self.open_file(filename)
        return self.handle_helper[filename].insert_record(data)

    def delete_data(self, filename, rid: RID):
        if filename not in self.handle_helper:
            self.open_file(filename)
        self.handle_helper[filename].delete_record(rid)

    def update_data(self, filename, data: np.ndarray, rid: RID):
        self.handle_helper[filename].update_record(data, rid)

    def get_data(self, filename, rid: RID):
        if filename not in self.handle_helper:
            self.open_file(filename)
        return self.handle_helper[filename].get_record(rid)

