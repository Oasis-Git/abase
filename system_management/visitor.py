from parser_management import SQLVisitor
from parser_management import SQLParser
from .result import Result
from .error import Error
from .processor import Processor
from information_management import *
from .selector import Selector
from const import const
import time


class Visitor(SQLVisitor):
    def __init__(self, processor: Processor):
        super().__init__()
        self.processor = processor
        self.clock = None

    def start_clock(self):
        self.clock = time.time()

    def run_time(self):
        return time.time() - self.clock

    def visitProgram(self, ctx: SQLParser.ProgramContext):
        results = []
        for statement in ctx.statement():
            try:
                self.start_clock()
                result: Result = statement.accept(self)
                cost = self.run_time()
                if result:
                    result.run_time = cost
                    results.append(result)
            except Error as e:
                # Once meet error, record result and stop visiting
                results.append(Result(e.msg, False, self.run_time(), 0))
                break
        return results

    def visitStatement(self, ctx:SQLParser.StatementContext):
        return self.visitChildren(ctx)

    def visitCreate_db(self, ctx:SQLParser.Create_dbContext):
        return self.processor.create_db(str(ctx.Identifier()))

    def visitErrorNode(self, node):
        raise Error('syntax error')

    def visitDrop_db(self, ctx:SQLParser.Drop_dbContext):
        return self.processor.drop_db(str(ctx.Identifier()))

    def visitUse_db(self, ctx:SQLParser.Use_dbContext):
        return self.processor.use_db(str(ctx.Identifier()))

    def visitShow_tables(self, ctx:SQLParser.Show_tablesContext):
        return self.processor.list_table()

    def visitCreate_table(self, ctx:SQLParser.Create_tableContext):
        index, primary_key, foreign_key, columns = self.visitField_list(ctx.field_list())
        table = TableInfo(str(ctx.Identifier()))
        table.columns = columns
        table.primary_keys = primary_key
        table.foreign_keys = foreign_key
        table.index = index
        return self.processor.create_new_table(table)

    def visitField_list(self, ctx:SQLParser.Field_listContext):
        index = []
        primary_key = []
        foreign_key = []
        columns = []
        primary_key_only = True
        for field in ctx.field():
            if isinstance(field, SQLParser.Normal_fieldContext):
                column, name = self.visitNormal_field(field)
                columns.append(column)
            elif isinstance(field, SQLParser.Primary_key_fieldContext) and primary_key_only:
                names = self.visitPrimary_key_field(field)
                for name in names:
                    primary_key.append(name)
                    index.append(name)
                primary_key_only = False
            elif isinstance(field, SQLParser.Primary_key_fieldContext) and not primary_key_only:
                raise Error(f'too many primary keys')
            else:
                field_name, table_name, refer_name = field.accept(self)
                for i in range(0, len(field_name)):
                    foreign_key.append((field_name[i], table_name, refer_name[i]))
                    index.append(field_name[i])
        return index, primary_key, foreign_key, columns

    def visitNormal_field(self, ctx:SQLParser.Normal_fieldContext):
        variable_type = self.visitType_(ctx.type_())
        column = ColumnInfo(str(ctx.Identifier()), variable_type)
        return column, str(ctx.Identifier())

    def visitPrimary_key_field(self, ctx:SQLParser.Primary_key_fieldContext):
        return ctx.identifiers().accept(self)

    def visitForeign_key_field(self, ctx:SQLParser.Foreign_key_fieldContext):
        return ctx.identifiers()[0].accept(self), ctx.children[6].getText(), ctx.identifiers()[1].accept(self)

    def visitType_(self, ctx:SQLParser.Type_Context):
        if str(ctx.getChild(0)) == 'INT':
            return VariableType.INT
        elif str(ctx.getChild(0)) == 'FLOAT':
            return VariableType.FLOAT
        return VariableType.VARCHAR

    def visitInsert_into_table(self, ctx:SQLParser.Insert_into_tableContext):
        table_name = str(ctx.Identifier())
        value_lists = ctx.value_lists().accept(self)
        for value_list in value_lists:
            self.processor.insert_value(table_name, value_list)
        return Result(('inserted_items: ' + str(len(value_lists))), True, None, 0)

    def visitValue_lists(self, ctx: SQLParser.Value_listsContext):
        return tuple(each.accept(self) for each in ctx.value_list())

    def visitValue_list(self, ctx: SQLParser.Value_listContext):
        return tuple(each.accept(self) for each in ctx.value())

    def visitValue(self, ctx: SQLParser.ValueContext):
        if ctx.Integer():
            return int(str(ctx.getText()))
        if ctx.Float():
            return float(str(ctx.getText()))
        if ctx.String():
            return str(ctx.getText())[1:-1]
        if ctx.Null():
            return None

    def close(self):
        self.processor.close()

    def visitSelect_table(self, ctx: SQLParser.Select_tableContext):
        table_names = ctx.identifiers().accept(self)
        selectors = ctx.selectors().accept(self)
        conditions = ctx.where_and_clause().accept(self) if ctx.where_and_clause() else {}
        for selector in selectors:
            if selector.table_name is None:
                selector.table_name = table_names
        for condition in conditions:
            if condition and condition['table_name'] is None:
                condition['table_name'] = table_names
        return self.processor.search(table_names[0], selectors, conditions)

    def visitSelectors(self, ctx:SQLParser.SelectorsContext):
        selectors = []
        if str(ctx.getChild(0)) == '*':
            selectors.append(Selector(const.SELECTOR_ALL, None, None))
            return selectors
        for item in ctx.selector():
            selectors.append(item.accept(self))
        return selectors

    def visitSelector(self, ctx:SQLParser.SelectorContext):
        table_name, column_name = ctx.column().accept(self)
        return Selector(const.SELECTOR_FIELD, table_name, column_name)

    def visitColumn(self, ctx:SQLParser.ColumnContext):
        if len(ctx.Identifier()) == 1:
            return None, str(ctx.Identifier(0))
        else:
            return str(ctx.Identifier(0)), str(ctx.Identifier(1))

    def visitWhere_and_clause(self, ctx: SQLParser.Where_and_clauseContext):
        conditions = []
        for where_and_clause in ctx.where_clause():
            conditions.append(where_and_clause.accept(self))
        return conditions

    def visitWhere_operator_expression(self, ctx:SQLParser.Where_operator_expressionContext):
        table_name, column_name = ctx.column().accept(self)
        operator = ctx.operator_().accept(self)
        lower_bound = None
        upper_bound = None
        if operator == '=':
            lower_bound = ctx.expression().accept(self)
            upper_bound = ctx.expression().accept(self)
        elif operator == '>':
            lower_bound = ctx.expression().accept(self)
            upper_bound = const.EDGE
        elif operator == '<':
            lower_bound = -const.EDGE
            upper_bound = ctx.expression().accept(self) - 1
        else:
            raise Error("unsolved function")
        return {'table_name': table_name, 'column_name': column_name, 'lower_bound': lower_bound,
                'upper_bound': upper_bound}

    def visitIdentifiers(self, ctx:SQLParser.IdentifiersContext):
        ret = []
        for i in ctx.Identifier():
            ret.append(str(i))
        return ret

    def visitOperator_(self, ctx:SQLParser.Operator_Context):
        return str(ctx.getText())

    def visitDelete_from_table(self, ctx:SQLParser.Delete_from_tableContext):
        table_name = str(ctx.Identifier())
        conditions = ctx.where_and_clause().accept(self)
        self.processor.delete(table_name, conditions)

    def visitAlter_add_index(self, ctx:SQLParser.Alter_add_indexContext):
        table_name = str(ctx.Identifier())
        column_names = ctx.identifiers().accept(self)
        for column_name in column_names:
            self.processor.create_new_index_with_data(table_name, column_name)
        return Result("new index created", True, None, 0)

    def visitAlter_drop_index(self, ctx:SQLParser.Alter_drop_indexContext):
        table_name = str(ctx.Identifier())
        column_names = ctx.identifiers().accept(self)
        for column_name in column_names:
            self.processor.delete_index(table_name, column_name)
        return Result(f"{len(column_names)} index deleted", True, None, 0)

    def visitAlter_table_add_pk(self, ctx:SQLParser.Alter_table_add_pkContext):
        table_name = str(ctx.Identifier(0))
        primary = ctx.identifiers().accept(self)
        self.processor.set_pk(table_name, primary)

    def visitAlter_table_drop_pk(self, ctx:SQLParser.Alter_table_drop_pkContext):
        table_name = str(ctx.Identifier())
        primary = ctx.identifiers().accept(self)
        self.processor.drop_pk(table_name, primary)
