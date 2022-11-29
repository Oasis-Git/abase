import os
from .error import Error
from .result import Result
from information_management import *
from record_management import *
from const import const
from index_management import *
from .selector import Selector
import numpy as np
import struct


class Processor:
    def __init__(self):
        self.path_header = os.getcwd() + '/data'
        self.current_path = None
        self.info_handle = None
        self.record_manager = RCManager()
        self.index_manager = IdManager()

    def create_db(self, token):
        if token in os.listdir(self.path_header):
            raise Error(f'Database {token} already exist')
        os.mkdir(self.path_header + f'/{token}')
        self.info_handle: InfoHandle = InfoHandle(True, token)
        self.info_handle.close()
        self.info_handle = None
        return Result(f'Database {token} created', True, None, 0)

    def drop_db(self, token):
        if token not in os.listdir(self.path_header):
            raise Error(f'Database {token} does not exist')
        os.rmdir(self.path_header + f'/{token}')
        return Result(f'Database {token} dropped', True, None, 0)

    def use_db(self, token):
        self.close()
        if token not in os.listdir(self.path_header):
            raise Error(f'Database {token} does not exist')
        self.current_path = self.path_header + f'/{token}'
        self.info_handle = InfoHandle(False, token)
        return Result(f'Database {token} using', True, None, 0)

    def list_table(self):
        table_name = os.listdir(self.current_path)
        ret = []
        for file in table_name:
            if file[:file.find('_')] not in ret:
                ret.append(file[:file.find('_')])
        return Result(f'{ret}', True, None, 1)

    def db_using(self):
        if self.info_handle is None:
            return None
        return self.info_handle.db_info.name

    def create_new_table(self, table: TableInfo):
        for f_k in table.foreign_keys:
            if f_k[1] not in self.info_handle.db_info.tables:
                raise Error(f'could not found table {f_k[1]}')
            if not self.table_check(f_k[1], [f_k[2]]):
                raise Error(f'could not found column {f_k[2]} in table {f_k[1]}')
        self.info_handle.db_info.insert_table(table)
        slot_size = self.total_size(table.columns)
        self.record_manager.create_file(self.info_handle.db_info.name + '/' + table.table_name + const.DATA_FILE,
                                        slot_size)
        for index_name in table.index:
            self.create_index(table.table_name, index_name)
        return Result(f'Table {table.table_name} created', True, None, 0)

    @staticmethod
    def total_size(columns):
        size = 0
        for column in columns:
            if column.variable_type == VariableType.VARCHAR:
                size += 256
            else:
                size += 4
        return size

    def create_index(self, table_name, variable_name):
        if self.info_handle:
            self.index_manager.create_index(table_name + '_' + variable_name, self.current_path)

    @staticmethod
    def get_type_size_list(columns):
        size_list = []
        type_list = []
        for column in columns:
            if column.variable_type == VariableType.VARCHAR:
                size_list.append(256)
                type_list.append(VariableType.VARCHAR)
            else:
                size_list.append(4)
                type_list.append(column.variable_type)
        return size_list, type_list

    def primary_check(self, table_name, value_list):
        ret = False
        for primary in self.info_handle.db_info.tables[table_name].primary_keys:
            index_ = -1
            for i, item in enumerate(self.info_handle.db_info.tables[table_name].columns):
                if primary == item.column_name:
                    index_ = i
            assert index_ != -1
            if not isinstance(value_list[index_], int):
                raise Error(f'invalid insert! {value_list[index_]} type unmatched')
            if table_name + '_' + primary not in self.index_manager.index_list.keys():
                self.index_manager.read_index(table_name + '_' + primary, self.current_path)
            if not self.index_manager.search(self.index_manager.index_list[table_name + '_' + primary],
                                             value_list[index_], value_list[index_]):
                ret = True
        return ret

    def insert_value(self, table_name, value_list):
        if not self.primary_check(table_name, value_list):
            raise Error('invalid primary key value')
        if not self.foreign_check(table_name, value_list):
            raise Error('foreign key missed')
        record_data = self.encode(table_name, value_list)
        rec = self.record_manager.insert_data(
            filename=self.info_handle.db_info.name + '/' + table_name + const.DATA_FILE,
            data=record_data)
        for index_name in self.info_handle.db_info.tables[table_name].index:
            pos = -1
            for i, column in enumerate(self.info_handle.db_info.tables[table_name].columns):
                if column.column_name == index_name:
                    pos = i
                    break
            assert pos != -1
            index_name = table_name + '_' + index_name
            if index_name not in self.index_manager.index_list:
                self.index_manager.read_index(index_name, self.current_path)
            self.index_manager.insert_rec(index_name, int(value_list[pos]), rec.record_id)

    def foreign_check(self, table_name, value_list):
        for key in self.info_handle.db_info.tables[table_name].foreign_keys:
            index_ = -1
            for i, item in enumerate(self.info_handle.db_info.tables[table_name].columns):
                if key[0] == item.column_name:
                    index_ = i
            assert index_ != -1
            index_name = key[1] + '_' + key[2]
            if index_name not in self.index_manager.index_list.keys():
                self.index_manager.read_index(index_name, self.current_path)
            if len(self.index_manager.search(self.index_manager.index_list[index_name], value_list[index_],
                                             value_list[index_])) == 0:
                return False
        return True

    def encode(self, table_name, value_list):
        total_length = self.total_size(self.info_handle.db_info.tables[table_name].columns)
        size_list, type_list = self.get_type_size_list(self.info_handle.db_info.tables[table_name].columns)
        record_data = np.zeros(total_length, dtype=np.uint8)
        pos = 0
        for size_, type_, value_ in zip(size_list, type_list, value_list):
            if type_ == VariableType.VARCHAR:
                if value_ is None:
                    length = 1
                    bytes_ = (1,)
                else:
                    if not isinstance(value_, str):
                        raise Error(f'invalid insert! {value_} type unmatched0')
                    bytes_ = (0,) + tuple(value_.encode())
                    length = len(bytes_)
                    if length > size_:
                        pass
                record_data[pos: pos + length] = bytes_
                record_data[pos + length: pos + size_] = 0
            elif type_ == VariableType.INT:
                if not isinstance(value_, int):
                    raise Error(f'invalid insert! {value_} type unmatched1')
                record_data[pos: pos + size_] = list(struct.pack('<i', value_))
            else:
                if not isinstance(value_, float):
                    raise Error(f'invalid insert! {value_} type unmatched2')
                record_data[pos: pos + size_] = list(struct.pack('<f', value_))
            pos += size_
        assert pos == total_length
        return record_data

    def decode(self, rec: Record, table_name):
        data = rec.record_data
        res = []
        pos = 0
        size_list, type_list = self.get_type_size_list(self.info_handle.db_info.tables[table_name].columns)
        for size_, type_ in zip(size_list, type_list):
            res.append(self.decode_help(data[pos: pos + size_], type_))
            pos += size_
        return res

    @staticmethod
    def decode_help(data, type_):
        if type_ == VariableType.VARCHAR:
            value = None if data[0] else data.tobytes()[1:].rstrip(b'\x00').decode('utf-8')
        elif type_ == VariableType.INT:
            value = struct.unpack('<i', data)[0]
        elif type_ == VariableType.FLOAT:
            value = struct.unpack('<f', data)[0]
        return value

    def close(self):
        self.index_manager.close(self.current_path)
        self.record_manager.close()
        if self.info_handle:
            self.info_handle.close()

    def table_check(self, table_name, column_names=None):
        if table_name not in self.info_handle.db_info.tables.keys():
            return False
        if column_names:
            for column_name in column_names:
                find = False
                for column in self.info_handle.db_info.tables[table_name].columns:
                    if column.column_name == column_name:
                        find = True
                        break
                if not find:
                    return False
        return True

    def search(self, table_name, selectors: list[Selector], conditions):
        if conditions:
            data_list = []
            for condition in conditions:
                if not self.table_check(table_name, [condition['column_name']]):
                    raise Error('invalid column!')
                if condition['column_name'] not in self.info_handle.db_info.tables[table_name].index:
                    all_data = self.search(table_name, [], None).msg
                    proper_data = self.condition_filter(table_name, conditions, all_data)
                    data_list = self.filter(selectors, proper_data, table_name)
                    return Result(data_list, True, None, 1)
                else:
                    ret_list = self.get_record(table_name, condition['column_name'], condition['lower_bound'],
                                               condition['upper_bound'])
                if len(data_list) == 0:
                    data_list.extend(ret_list)
                else:
                    data_list = list(set(data_list).intersection(set(ret_list)))
        else:
            data_list = self.get_record(table_name, self.info_handle.db_info.tables[table_name].primary_keys[0],
                                        -const.EDGE, const.EDGE)
        data_list = [self.decode(rec, table_name) for rec in data_list]
        data_list = self.filter(selectors, data_list, table_name)
        for i in data_list:
            print(i)
        return Result(data_list, True, None, 1)

    def condition_filter(self, table_name, conditions, all_data):
        ret = []
        for data in all_data:
            suc = True
            for condition in conditions:
                index_ = self.find_index_by_column(table_name, condition['column_name'])
                if not (data[index_] >= int(condition['lower_bound'] and data[index_] <= condition['upper_bound'])):
                    suc = False
                    break
            if suc:
                ret.append(data)
        return ret

    def filter(self, selectors: list[Selector], data_list, table_name):
        if len(selectors) == 0 or selectors[0].type_ == const.SELECTOR_ALL:
            return data_list
        else:
            index_list = []
            for selector in selectors:
                for i, item in enumerate(self.info_handle.db_info.tables[table_name].columns):
                    if not self.table_check(table_name, [selector.column_name]):
                        raise Error('invalid column!')
                    if item.column_name == selector.column_name:
                        index_list.append(i)
                        break
            assert len(index_list) == len(selectors)
            ret = []
            for data in data_list:
                appending = []
                for index_ in index_list:
                    appending.append(data[index_])
                ret.append(appending)
            return ret

    def get_record(self, table_name, index_name, lower_bound, upper_bound):
        index_name = table_name + '_' + index_name
        if index_name not in self.index_manager.index_list:
            self.index_manager.read_index(index_name, self.current_path)
        list_rid = self.index_manager.search(self.index_manager.index_list[index_name], lower_bound, upper_bound)
        path = self.info_handle.db_info.name + '/' + table_name + const.DATA_FILE
        list_data = [self.record_manager.get_data(path, rid) for rid in list_rid]
        return list_data

    def get_rid_and_keys(self, table_name, index_name, lower_bound, upper_bound):
        index_name = table_name + '_' + index_name
        if index_name not in self.index_manager.index_list:
            self.index_manager.read_index(index_name, self.current_path)
        return self.index_manager.search_both(self.index_manager.index_list[index_name], lower_bound, upper_bound)

    def find_index_by_column(self, table_name, column_name):
        for i, column in enumerate(self.info_handle.db_info.tables[table_name].columns):
            if column_name == column.column_name:
                return i
        return -1

    def delete(self, table_name, conditions):
        data_list = self.search(table_name, [], conditions).msg
        index_list = []
        for primary in self.info_handle.db_info.tables[table_name].primary_keys:
            index_list.append(self.find_index_by_column(table_name, primary))
        for data in data_list:
            conflict_num = 0
            for index_ in index_list:
                if self.find_index_by_column(table_name, data[index_]):
                    conflict_num += 1
            if conflict_num == len(index_list):
                raise Error('foreign key reason for delete error')
        collect = False
        pre_for_delete = []
        for index_name in self.info_handle.db_info.tables[table_name].index:
            index_ = self.find_index_by_column(table_name, index_name)
            index_name = table_name + '_' + index_name
            if index_name not in self.index_manager.index_list:
                self.index_manager.read_index(index_name, self.current_path)
            for data in data_list:
                if not collect:
                    rec = self.index_manager.search(index_name, data[index_], data[index_])
                    pre_for_delete.append(rec)
                self.index_manager.delete_rec(index_name, data[index_])
            collect = True
        for rid_ in pre_for_delete:
            self.record_manager.delete_data(self.info_handle.db_info.name + '/' + table_name + const.DATA_FILE,
                                            rid_)
        return Result(f"{len(pre_for_delete)} items deleted", True, None, 0)

    def find_conflict_delete(self, variable_name, value):
        for table in self.info_handle.db_info.tables.values:
            for f_k in table.foreign_keys:
                if f_k[2] == variable_name:
                    index_name = table.table_name + '_' + variable_name
                    if index_name not in self.index_manager.index_list:
                        self.index_manager.read_index(index_name, self.current_path)
                    if len(self.index_manager.search(index_name, value, value)) != 0:
                        return True
                    break
        return False

    def create_new_index_with_data(self, table_name, variable_name):
        if not self.table_check(table_name, [variable_name]):
            raise Error(f'invalid column {variable_name}')
        index_name = table_name + '_' + variable_name
        if self.info_handle:
            self.index_manager.create_index(index_name, self.current_path)
        data_list = self.get_record(table_name, self.info_handle.db_info.tables[table_name].primary_keys[0],
                                    -const.EDGE, const.EDGE)
        rid_list = [rec.record_id for rec in data_list]
        data_list = [self.decode(rec, table_name) for rec in data_list]
        index_ = -1
        for i, item in enumerate(self.info_handle.db_info.tables[table_name].columns):
            if variable_name == item.column_name:
                index_ = i
        assert index_ != -1
        assert len(rid_list) == len(data_list)
        if index_name not in self.index_manager.index_list:
            self.index_manager.read_index(index_name, self.current_path)
        for i in range(0, len(rid_list)):
            self.index_manager.insert_rec(index_name, data_list[i][index_], rid_list[i])
        self.info_handle.db_info.tables[table_name].index.append(variable_name)

    def delete_index(self, table_name, variable_name):
        if not self.table_check(table_name, [variable_name]):
            raise Error(f'invalid column {variable_name}')
        if variable_name not in self.info_handle.db_info.tables[table_name].index:
            raise Error(f'{variable_name} not in index of Table {table_name} ')
        self.index_manager.destroy_index(table_name + '_' + variable_name, self.current_path)
        self.info_handle.db_info.tables[table_name].index.remove(variable_name)

    def drop_pk(self, table_name, primary):
        if primary == self.info_handle.db_info.tables[table_name].primary_keys:
            self.info_handle.db_info.tables[table_name].fake_primary = True

    def set_pk(self, table_name, primary):
        if not self.info_handle.db_info.tables[table_name].fake_primary:
            raise Error('primary key exist')
        for key in primary:
            self.create_index(table_name, key)
            index_name = table_name + '_' + key
            if index_name not in self.index_manager.index_list.keys():
                self.index_manager.read_index(index_name, self.current_path)
            if not self.index_manager.index_list[index_name].check_single:
                pass
