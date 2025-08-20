import sympy
from .geometry import *

class Solver:
    def __init__(self):
        self.symbols = {}
        self.constraints = []
        self.equations = []
        
    def add_object(self, name, obj):
        self.symbols[name] = obj
        
    def add_constraint(self, left, op, right):
        if op == '==':
            self.constraints.append(sympy.Eq(left.as_sympy(), right.as_sympy()))
        
    def solve(self):
        if not self.constraints:
            return {}
        return sympy.solve(self.constraints, self.all_symbols(), dict=True)
    
    def all_symbols(self):
        syms = set()
        for obj in self.symbols.values():
            syms |= obj.symbols()
        return list(syms)