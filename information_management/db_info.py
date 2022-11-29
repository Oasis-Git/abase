from .table_info import *


class DbInfo:
    def __init__(self, dbname):
        self.tables = {}
        self.name = dbname

    def insert_table(self, table_info: TableInfo):
        self.tables[table_info.table_name] = table_info

    def delete_table(self, table_name):
        if table_name in self.tables:
            self.tables.pop(table_name)
