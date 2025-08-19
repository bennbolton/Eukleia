import sympy
from .geometry import *

class Solver:
    def __init__(self):
        self.objects = {}
        self.constraints = []
        self.equations = []
        
    def add_object(self, name, obj):
        self.objects[name] = obj
        
    def add_constraint(self, constraint):
        self.constraints.append(constraint)
        self._update_symbolic(constraint)
        
    def evaluate_constraints(self):
        
        for c in self.constraints:
            pass