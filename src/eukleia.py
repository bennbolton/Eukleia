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

    def run(self, code, spit=False):
        self.tokens = self.lexer.generate_tokens(code)
        
        if spit:
            print("TOKENS:")
            print(self.tokens)
        
        self.astNodes = self.parser.parseTokens(self.tokens)
        
        if spit:
            print("NODES:")
            for node in self.astNodes:
                print(repr(node))
        
        self.interpreter.run(self.astNodes)

        
        



        