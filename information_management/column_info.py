from enum import Enum


class VariableType(Enum):
    INT = 4
    FLOAT = 8
    VARCHAR = 256


class ColumnInfo:
    def __init__(self, column_name, variable_type: VariableType, index=False):
        self.column_name = column_name
        self.variable_type = variable_type
        self.index = index
