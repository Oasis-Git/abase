from .column_info import *


class TableInfo:
    def __init__(self, table_name):
        self.table_name = table_name
        self.columns = []
        self.index = []
        self.foreign_keys = []
        self.primary_keys = []
        self.fake_primary = False

    def insert_column(self, column: ColumnInfo):
        self.columns.append(column)

    def set_primary_keys(self, column_name):
        if column_name in self.columns:
            self.primary_keys.append(column_name)

    def set_foreign_keys(self, column_name):
        if column_name in self.columns:
            self.foreign_keys.append(column_name)

    def set_index(self, column_name):
        if column_name in self.columns:
            self.index.append(column_name)
