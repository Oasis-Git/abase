from .rid import RID
from .record import Record
from const import const
from file_management.bufpagemanager import BufPageManager
import numpy as np
import json


class RCHandler:
    def __init__(self, file_id, file_manager: BufPageManager):
        self.file_id = file_id
        self.file_manager = file_manager
        self.bit_map_size = const.BIT_MAP_SIZE
        json_data = file_manager.read_page(self.file_id, 0)
        json_data = json_data.decode('utf-8').rstrip('\0')
        info = json.loads(json_data)
        self.page_num = info['page_num']
        self.valid_page = info['valid_page']
        self.slot_size = info['slot_size']      # bytes
        self.max_slot_num = (const.PAGE_SIZE - 32) // self.slot_size

    def close(self):
        return {'page_num': self.page_num, 'valid_page': self.valid_page, 'slot_size': self.slot_size}

    def cal_begin(self, slot_id):
        return self.bit_map_size/8 + self.slot_size*slot_id

    @staticmethod
    def map_pos_val(slot_id, enable: bool):
        if enable:
            return slot_id//32, 1 << (slot_id % 32)
        else:
            return slot_id//32, ~(1 << (slot_id % 32))

    def new_page(self):
        default = np.zeros(256)
        default = default.tobytes()
        self.page_num += 1
        self.valid_page += 1
        self.file_manager.write_page(self.file_id, self.page_num-1, default)

    def get_record(self, record_id: RID):
        data = np.frombuffer(self.file_manager.read_page(self.file_id, record_id.get_page_id()), np.uint8, -1)
        slot_begin = self.cal_begin(record_id.get_slot_id())

        data = data[int(slot_begin):
                    int(slot_begin + self.slot_size)]
        rec = Record(record_id, data)
        return rec

    def delete_record(self, record_id: RID):
        data = np.frombuffer(self.file_manager.read_page(self.file_id, record_id.get_page_id()), np.uint8, -1)
        data = data.copy()
        slot_begin = self.cal_begin(record_id.get_slot_id())
        for index in range(int(slot_begin), int(slot_begin + self.slot_size)):
            data[index] = 0
        pos, val = self.map_pos_val(record_id.slot_id, False)
        data[pos] &= val
        self.file_manager.write_page(self.file_id, record_id.get_page_id(), data)

    def insert_record(self, data):
        page_id = self.valid_page
        page_data = np.frombuffer(self.file_manager.read_page(self.file_id, page_id), np.uint8, -1)
        page_data = page_data.copy()
        for index in range(0, self.max_slot_num):
            pos_in, val = self.map_pos_val(index, True)
            if page_data[pos_in] & val == 0:
                page_data.data[pos_in] |= val
                begin_pos = self.cal_begin(index)
                for length in range(0, self.slot_size):
                    page_data[int(length + begin_pos)] = data[int(length)]
                self.file_manager.write_page(self.file_id, page_id, page_data.tobytes())
                record = Record(RID(page_id, index), data)
                return record
        self.new_page()
        return self.insert_record(data)

    def update_record(self, record_id: RID, data: np.ndarray):
        page_data = np.frombuffer(self.file_manager.read_page(self.file_id, record_id.get_page_id()), np.uint8, -1)
        begin_pos = self.cal_begin(record_id.get_slot_id())
        for length in range(0, self.slot_size):
            page_data[length + begin_pos] = data[length]
        self.file_manager.write_page(self.file_id, record_id.page_id, page_data.tobytes())
        return Record(record_id, data)
