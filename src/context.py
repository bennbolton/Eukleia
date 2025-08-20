from src.lexer import Lexer
from src.parser import Parser
from .interpreter import Interpreter
from .solver import Solver


class ExecutionContext:
    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser()
        self.solver = Solver()
        self.interpreter = Interpreter(self.solver)
        