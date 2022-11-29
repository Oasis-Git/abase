from antlr4 import InputStream, CommonTokenStream
from antlr4.error.Errors import ParseCancellationException
from antlr4.error.ErrorListener import ErrorListener

from parser_management import SQLParser
from parser_management import SQLLexer
from .visitor import Visitor
from .processor import Processor
from .result import Result
from .error import Error


class SystemManager:
    def __init__(self):
        self.visitor = Visitor(Processor())

    def execute(self, sql):
        # class Strategy(BailErrorStrategy):
        #     def recover(self, recognizer, e):
        #         recognizer._errHandler.reportError(recognizer, e)
        #         super().recover(recognizer, e)

        class StringErrorListener(ErrorListener):
            def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
                raise ParseCancellationException("line " + str(line) + ":" + str(column) + " " + msg)

        input_stream = InputStream(sql)
        lexer = SQLLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(StringErrorListener())
        tokens = CommonTokenStream(lexer)
        parser = SQLParser(tokens)
        parser.removeErrorListeners()
        parser.addErrorListener(StringErrorListener())
        try:
            tree = parser.program()
        except ParseCancellationException as e:
            print(e)
            return [Result('syntax error', False, 0, 0)]
        try:
            return self.visitor.visit(tree)
        except Error as e:
            return [Result(e.msg, False, 0, 0)]

    def close(self):
        self.visitor.close()

    def database_using(self):
        return self.visitor.processor.db_using()
