from src.lexer import Lexer
from src.parser import Parser
from .interpreter import Interpreter
from .solver import Solver


class Eukleia:
    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser()
        self.solver = Solver()
        self.interpreter = Interpreter(self)

    def run(self, code):
        self.tokens = self.lexer.generate_tokens(code)

        self.astNodes = self.parser.parseTokens(self.tokens)

        self.interpreter.run(self.astNodes)


        