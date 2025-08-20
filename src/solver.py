import sympy as sp
from .geometry import *
import copy
COUNT = 0
class SolutionSet:
    def __init__(self, solvers=None):
        self.solvers = solvers if solvers else [Solver()]

    def refine(self):
        """
        Eagerly solve/branch *in place*.

        For each solver in the current set:
        - If there are no solutions (or nothing new), keep it as-is.
        - If there is exactly one solution, apply it in-place.
        - If there are multiple, clone and apply each, producing branches.

        After processing all solvers, replace `self.solvers` with the new list.
        """
        new_solvers = []

        for solver in self.solvers:
            sols = solver.solve()

            # Normalise various SymPy return shapes
            if sols is None:
                sols = []
            elif isinstance(sols, dict):
                sols = [sols]

            if not sols:
                # Nothing to apply / underdetermined: keep this branch as-is
                new_solvers.append(solver)
                continue
            # print(solver.symbols['C'])
            if len(sols) == 1:
                # Apply directly to this branch
                solver.apply_solution(sols[0])
                new_solvers.append(solver)
            else:
                # Branch for each solution
                for sol in sols:
                    branched = solver.clone()
                    branched.apply_solution(sol)
                    new_solvers.append(branched)
            # print(solver.symbols['C'])
        self.solvers = new_solvers
        return self
    
    def add_object(self, name, obj):
        for solver in self.solvers:
            solver.add_object(name, obj)
    
    def add_constraint(self, left, op, right):
        for solver in self.solvers:
            solver.add_constraint(left, op, right)
        self.refine()

    def reference(self, referenceNode):
        unique_values = self.get_symbol_possibilities(referenceNode)
        if len(unique_values) == 1:
            return unique_values[0]
        else:
            return referenceNode
        
    def get_symbol_possibilities(self, referenceNode):
        values = []
        for solver in self.solvers:
            obj = solver.symbols.get(referenceNode.name)
            if obj is not None:
                values.append(obj)
        # Remove duplicates (using repr for equality)
        unique_values = []
        seen = set()
        for val in values:
            rep = repr(val)
            if rep not in seen:
                unique_values.append(val)
                seen.add(rep)
        return unique_values




class Solver:
    def __init__(self):
        self.symbols = {}
        self.constraints = []
        
    def add_object(self, name, obj):
        self.symbols[name] = obj
        
    def add_constraint(self, left, op, right):
        
        if op == '==':
            compareValue = {
                Angle: 'as_sympy',
                Line: 'length',
                Number: 'as_sympy'
            }
            self.constraints.append(sp.Eq(getattr(left, compareValue[type(left)])(), (getattr(right, compareValue[type(right)])())))
            # # Angle size constraint: <ABC == 90
            # if isinstance(left, Angle):
            #     self.constraints.append(sp.Eq(left.as_sympy(), right.as_sympy()))
            # # Line length constraint: AB == CD
            # elif isinstance(left, Line):
            #     if isinstance(right, Line):
            #         self.constraints.append(sp.Eq(left.length_squared(), right.length_squared()))
            #     elif
        
    def clone(self):
        new_solver = Solver()
        new_solver.symbols = {name: copy.deepcopy(obj) for name, obj in self.symbols.items()}
        new_solver.constraints = copy.deepcopy(self.constraints)
        return new_solver
    
    def solve(self):
        if not self.constraints:
            return {}
        return sp.solve(self.constraints, self.all_symbols(), dict=True)
        
    def apply_solution(self, solution):
        # Needs optimizing
        for obj in self.symbols.values():
            obj.substitute(solution)
                    

         
    
    def all_symbols(self):
        syms = set()
        for obj in self.symbols.values():
            syms |= obj.symbols()
        return list(syms)