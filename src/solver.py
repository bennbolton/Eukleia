from .geometry import *
from .rules import *
from itertools import combinations
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
        self.points: dict[str, any] = {}
        self.constraints: list[Constraint] = []
        self.rules = [rule() for rule in GeometricRule.__subclasses__()]
        self.consRules = [rule() for rule in DefinitionRule.__subclasses__()]
        self.facts = Facts()

    def add_point(self, obj):
        name = getattr(obj, "name", None)
        if name and name not in self.points:
            self.points[obj.name] = obj

    def add_constraint(self, constraint:Constraint):
        self.constraints.append(constraint)


    def create_triangles(self):
        for comb in combinations(self.points.values(), 3):
            if len(set(comb)) < 3:
                continue
            key = frozenset(comb)
            tri = Triangle(comb)
            if key not in self.facts.triangles and not tri.is_degenerate(self.facts):
                self.facts.triangles[key] = tri
        


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


        agenda = []
        for con in self.constraints:
            for rule in self.consRules:
                if con.consType() == rule.kind:
                    changed_values = rule.apply(con, self.facts)
                    if changed_values is not None:
                        agenda[0:0] = changed_values

        self.create_triangles()

        while agenda:
            obj = agenda.pop()
            for rule in self.rules:               
                if type(obj).__name__ in rule.kind:
                    changed_values = rule.apply(obj, self.facts)
                    if changed_values is not None:
                        agenda[0:0] = changed_values
                        for value in changed_values:
                            for tri in rule.getTriangles(value, self.facts):
                                if tri.is_degenerate(self.facts):
                                    self.facts.triangles.pop(frozenset(tri.points), None)
            if canStop(targets):
                return {t: self.facts.get_value(t) for t in targets}
        return {t: self.facts.get_value(t) or "Undeterminable" for t in targets}