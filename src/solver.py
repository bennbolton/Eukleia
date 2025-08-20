import sympy as sp
from .geometry import *
import copy
COUNT = 0
class Solver:
    def __init__(self, sets=None):
        self.solution_sets = sets if sets else [SolutionSet()]

    def refine(self):
        """
        Eagerly solve/branch *in place*.

        For each solver in the current set:
        - If there are no solutions (or nothing new), keep it as-is.
        - If there is exactly one solution, apply it in-place.
        - If there are multiple, clone and apply each, producing branches.

        After processing all solvers, replace `self.solvers` with the new list.
        """
        new_sets = []

        for sol_set in self.solution_sets:
            sols = sol_set.solve()

            # Normalise various SymPy return shapes
            if sols is None:
                sols = []
            elif isinstance(sols, dict):
                sols = [sols]

            if not sols:
                # Nothing to apply / underdetermined: keep this branch as-is
                new_sets.append(sol_set)
                continue
            # print(solver.symbols['C'])
            if len(sols) == 1:
                # Apply directly to this branch
                sol_set.apply_solution(sols[0])
                new_sets.append(sol_set)
            else:
                # Branch for each solution
                for sol in sols:
                    branched = sol_set.clone()
                    branched.apply_solution(sol)
                    new_sets.append(branched)
            # print(solver.symbols['C'])
        self.solution_sets = new_sets
        return self
    
    def add_object(self, name, obj):
        for sol_set in self.solution_sets:
            sol_set.add_object(name, obj)
    
    def add_constraint(self, left, op, right):
        for sol_set in self.solution_sets:
            sol_set.add_constraint(left, op, right)
        self.refine()

    def reference(self, referenceNode):
        unique_values = self.get_symbol_possibilities(referenceNode)
        if len(unique_values) == 1:
            return unique_values[0]
        else:
            return referenceNode
        
    def get_symbol_possibilities(self, referenceNode):
        values = []
        for sol_set in self.solution_sets:
            obj = sol_set.symbols.get(referenceNode.name)
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




class SolutionSet:
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
        
    def clone(self):
        new_sol_set = SolutionSet()
        new_sol_set.symbols = {name: copy.deepcopy(obj) for name, obj in self.symbols.items()}
        new_sol_set.constraints = copy.deepcopy(self.constraints)
        return new_sol_set
    
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