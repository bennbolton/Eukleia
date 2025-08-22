import sympy as sp
from .geometry import *
import copy
class Solver:
    def __init__(self, branches=None):
        self.branches = branches if branches else [SolverBranch()]
    
    def add_branches(self, new_branches):
        for branch in new_branches:
            if not any([branch == existing for existing in self.branches]):
                self.branches.append(branch)

    def prune(self):
        self.branches = list(filter(lambda x: x.is_valid(), self.branches))

    




class SolverBranch:
    def __init__(self):
        self.symbols = {}
        self.constraints = []
        self.symbol_map = {}
        self.fullyDefined = False
        
    def add_object(self, name, obj):
        self.symbols[name] = obj
        
    def add_constraint(self, left, op, right):
        if op == '==':
            compareValue = {
                Angle: 'cos',
                Line: 'length',
                Number: 'as_sympy'
            }
            print(left, right)
            if isinstance(left, Angle):
                self.constraints.append(sp.Eq(left.as_sympy(), right.as_sympy()))
            else:
            # self.constraints.append(sp.Eq(left.cross(), sp.sqrt(left.dot()**2 + left.cross()**2)*sp.sin(right.as_sympy())))
            # if isinstance(left, Angle) and isinstance(right, Number):
            #     self.constraints.append(left == right)
            # else:
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
        elif op == '//':
            if not (isinstance(left, Line) and isinstance(right, Line)):
                raise ValueError(f"Objects of type {type(left)} and {type(right)} cannot be parallel")
            dirB_A = left.direction()
            dirD_C = right.direction()
            expr = dirB_A[0]*dirD_C[1] - dirB_A[1]*dirD_C[0]
            self.constraints.append(sp.Eq(expr, 0))
        
        refined_branches = self.refine()
        valid_branches = list(filter(lambda x: x.is_valid(), refined_branches))
        if not valid_branches:
            raise ValueError(
                f'Impossible constraint: {left} {op} {right}\n'
            )
        return valid_branches
    
    def __eq__(self, other):
        if isinstance(other, SolverBranch):
            return self.symbol_map == other.symbol_map
        
    
    def refine(self):

        for c in self.constraints:
            if isinstance(c, sp.Or):
                new_branches = []
                for option in c.args:
                    branched = self.clone()
                    branched.constraints.remove(c)
                    branched.constraints.append(option)
                    new_branches.extend(branched.refine())
                return new_branches

        new_branches = []
        sols = self.solve()
        # Normalise various SymPy return shapes
        if sols is None:
            sols = []
        elif isinstance(sols, dict):
            sols = [sols]

        if not sols:
            new_branches.append(self.clone())
            return new_branches
      
        # Branch for each solution
        for sol in sols:
            branched = self.clone()
            branched.apply_solution(sol)

            new_branches.append(branched)
        return new_branches
        
        
    def clone(self):
        new_branch = SolverBranch()
        new_branch.symbols = {name: copy.deepcopy(obj) for name, obj in self.symbols.items()}
        new_branch.constraints = copy.deepcopy(self.constraints)
        new_branch.symbol_map = copy.deepcopy(self.symbol_map)
        return new_branch
    
    def solve(self):
        if not self.constraints:
            return {}
        
        eqs = []
        ineqs = []
        for c in self.constraints:
            if (isinstance(c, sp.Equality)): eqs.append(c)
            else: ineqs.append(c)
        sols = sp.solve(eqs, self.all_symbols(), dict=True)
        valid_sols = [sol for sol in sols if all([bool(ineq.subs(sol)) for ineq in ineqs])]
        return valid_sols

    def apply_solution(self, solution):
        # Needs optimizing
        for obj in self.symbols.values():
            obj.substitute(solution)
        for sym, val in solution.items():
            self.symbol_map[sym] = val
        

                    
    def all_symbols(self):
        syms = set()
        for obj in self.symbols.values():
            syms |= obj.symbols()
        return list(syms)
    
    def is_valid(self):
        constraints = copy.deepcopy(self.constraints)

        eqs = []
        ineqs = []
        for c in constraints:
            if (isinstance(c, sp.Equality)): eqs.append(c)
            else: ineqs.append(c)

        for eq in eqs:
            try:
                simplified = sp.simplify(eq.subs(self.symbol_map))
                
                if simplified == False: return False
            except Exception:
                continue

        for ineq in ineqs:
            try: 
                simplified = sp.simplify(ineq.subs(self.symbol_map))
                if simplified == False: return False
            except Exception:
                continue
                
        return True
    