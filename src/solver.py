from .geometry import *
from .rules import *
class Solver:
    def __init__(self):
        self.branches = [SolverBranch()]
    pass

    def solve(self, targets):
        solutions = {}
        for branch in self.branches:
            sols = branch.solve(targets)
            for target in targets:
                solutions.setdefault(target, []).append(sols[target])
        return solutions

class SolverBranch:
    def __init__(self):
        self.symbols: dict[str, any] = {}
        self.constraints: list[Constraint] = []
        self.rules = [rule() for rule in GeometricRule.__subclasses__()]
        self.facts = Facts()

    def add_symbol(self, obj):
        name = getattr(obj, "name", None)
        if name and name not in self.symbols:
            self.symbols[obj.name] = obj

    def add_constraint(self, constraint:Constraint):
        self.constraints.append(constraint)
        for side in ("left", "right"):
            obj = getattr(constraint, side)
            if isinstance(obj, Angle):
                self.ensure_trianle(obj)

    def ensure_trianle(self, angle: Angle):
        key = frozenset(angle.points)
        if key not in self.facts.triangles:
            self.facts.triangles[key] = Triangle(angle.points)
        return self.facts.triangles[key]

    def solve(self, targets):
        def canStop(targets):
            for target in targets:
                if isinstance(target, Line):
                    if self.facts.get_segment_value(target) is None:
                        return False
                elif isinstance(target, Angle):
                    if self.facts.get_angle_value(target) is None:
                        return False
            return True


        agenda = [con for con in self.constraints]
        while agenda:
            con = agenda.pop()
            for rule in self.rules:
                if isinstance(con, Constraint):
                    if con.consType() == rule.kind:
                        changed_values = rule.apply(con, self.facts)
                        if changed_values is not None:
                            agenda.insert(0,changed_values)
                    
                else:
                    if type(con).__name__ == rule.kind:
                        changed_values = rule.apply(con, self.facts)
                        if changed_values is not None:
                            agenda.insert(0,changed_values)
            if canStop(targets):
                return {t: self.facts.get_value(t) for t in targets}