import sympy as sp
from .geometry import *
import copy
class Solver:
    def __init__(self, branches=None):
        self.branches = branches if branches else [SolverBranch()]

    def refine(self):
        """
        Eagerly solve/branch *in place*.

        For each solver in the current set:
        - If there are no solutions (or nothing new), keep it as-is.
        - If there is exactly one solution, apply it in-place.
        - If there are multiple, clone and apply each, producing branches.

        After processing all solvers, replace `self.solvers` with the new list.
        """
        new_branches = []
        for branch in self.branches:
            sols = branch.solve()

            # Normalise various SymPy return shapes
            if sols is None:
                sols = []
            elif isinstance(sols, dict):
                sols = [sols]

            if not sols:
                # Nothing to apply / underdetermined: keep this branch as-is
                new_branches.append(branch)
                continue
            if len(sols) == 1:
                # Apply directly to this branch
                branch.apply_solution(sols[0])
                new_branches.append(branch)
            else:
                # Branch for each solution
                for sol in sols:
                    branched = branch.clone()
                    branched.apply_solution(sol)
                    new_branches.append(branched)
        self.branches = new_branches
        return self
    
    def add_object(self, name, obj):
        for branch in self.branches:
            branch.add_object(name, obj)
    
    def add_constraint(self, left, op, right):
        for branch in self.branches:
            branch.add_constraint(left, op, right)
        self.refine()


    def reference(self, referenceNode):
        unique_values = self.get_symbol_possibilities(referenceNode)
        if len(unique_values) == 1:
            return unique_values[0]
        else:
            return referenceNode
        
    def get_symbol_possibilities(self, referenceNode):
        values = []
        for branch in self.branches:
            obj = branch.symbols.get(referenceNode.name)
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




class SolverBranch:
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
        elif op[-2:] == 'on':
            if isinstance(left, Point) and isinstance(right, Line):
                A, B = right.A, right.B
                Px, Py = left.x.as_sympy(), left.y.as_sympy()
                Ax, Ay = A.x.as_sympy(), A.y.as_sympy()
                Bx, By = B.x.as_sympy(), B.y.as_sympy()
                expr = (Bx - Ax) * (Py - Ay) - (By - Ay) * (Px - Ax)
                if op == 'NOT_on':
                    self.constraints.append(sp.Ne(expr, 0))
                else:
                    self.constraints.append(sp.Eq(expr, 0))
            else:
                raise ValueError("Currently unsupported 'on' between {left} and {right}")
        
        
    def clone(self):
        new_sol_set = SolverBranch()
        new_sol_set.symbols = {name: copy.deepcopy(obj) for name, obj in self.symbols.items()}
        new_sol_set.constraints = copy.deepcopy(self.constraints)
        return new_sol_set
    
    def solve(self):
        if not self.constraints:
            return {}
        sols = sp.solve(self.constraints, self.all_symbols(), dict=True)
        return sols

    def apply_solution(self, solution):
        # Needs optimizing
        for obj in self.symbols.values():
            obj.substitute(solution)
                    
    def all_symbols(self):
        syms = set()
        for obj in self.symbols.values():
            syms |= obj.symbols()
        return list(syms)
    
    