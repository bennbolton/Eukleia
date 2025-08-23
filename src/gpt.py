# =====================================================================
# Key helpers for segment and angle keys
# =====================================================================

def seg_key(a, b):
    """Undirected segment: AB == BA"""
    return tuple(sorted((str(a), str(b))))

def ang_key(a, b, c):
    """Angle at vertex b"""
    return (str(a), str(b), str(c))

# =====================================================================
# Union-Find (disjoint set) with value storage
# =====================================================================

class DSU:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            return x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return ra
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return ra

# =====================================================================
# Facts store: keeps equalities + optional numeric values
# =====================================================================

class Facts:
    def __init__(self):
        self.seg_dsu = DSU()
        self.ang_dsu = DSU()
        self.seg_val = {}  # rep -> value
        self.ang_val = {}

    # --- Segments ---
    def merge_segments(self, s1, s2):
        r1, r2 = self.seg_dsu.find(s1), self.seg_dsu.find(s2)
        if r1 == r2:
            return False
        v1, v2 = self.seg_val.get(r1), self.seg_val.get(r2)
        r = self.seg_dsu.union(r1, r2)
        if v1 is not None and v2 is not None and abs(v1 - v2) > 1e-12:
            raise ValueError("Impossible constraint: segment values conflict")
        if v1 is not None:
            self.seg_val[r] = v1
        if v2 is not None:
            self.seg_val[r] = v2
        return True

    def set_segment_value(self, s, val):
        r = self.seg_dsu.find(s)
        v = self.seg_val.get(r)
        if v is None:
            self.seg_val[r] = float(val)
            return True
        if abs(v - val) > 1e-12:
            raise ValueError("Impossible constraint: segment already has different value")
        return False

    def get_segment_value(self, s):
        return self.seg_val.get(self.seg_dsu.find(s))

    # --- Angles ---
    def merge_angles(self, a1, a2):
        r1, r2 = self.ang_dsu.find(a1), self.ang_dsu.find(a2)
        if r1 == r2:
            return False
        v1, v2 = self.ang_val.get(r1), self.ang_val.get(r2)
        r = self.ang_dsu.union(r1, r2)
        if v1 is not None and v2 is not None and abs(v1 - v2) > 1e-10:
            raise ValueError("Impossible constraint: angle values conflict")
        if v1 is not None:
            self.ang_val[r] = v1
        if v2 is not None:
            self.ang_val[r] = v2
        return True

    def set_angle_value(self, a, deg):
        r = self.ang_dsu.find(a)
        v = self.ang_val.get(r)
        if v is None:
            self.ang_val[r] = float(deg)
            return True
        if abs(v - deg) > 1e-10:
            raise ValueError("Impossible constraint: angle already has different value")
        return False

    def get_angle_value(self, a):
        return self.ang_val.get(self.ang_dsu.find(a))

# =====================================================================
# Rule base
# =====================================================================

class LengthEqualityRule:
    kind = 'length_eq'
    def apply(self, cons, facts):
        _, left, right = cons
        changed = False
        if left[0] == 'seg' and right[0] == 'seg':
            changed |= facts.merge_segments(seg_key(left[1], left[2]), seg_key(right[1], right[2]))
        elif left[0] == 'seg' and right[0] == 'val':
            changed |= facts.set_segment_value(seg_key(left[1], left[2]), right[1])
        elif right[0] == 'seg' and left[0] == 'val':
            changed |= facts.set_segment_value(seg_key(right[1], right[2]), left[1])
        elif left[0] == 'val' and right[0] == 'val':
            if abs(left[1] - right[1]) > 1e-12:
                raise ValueError("Impossible constraint: values differ")
        return changed

class AngleEqualityRule:
    kind = 'angle_eq'
    def apply(self, cons, facts):
        _, left, right = cons
        changed = False
        if left[0] == 'ang' and right[0] == 'ang':
            changed |= facts.merge_angles(ang_key(left[1], left[2], left[3]),
                                          ang_key(right[1], right[2], right[3]))
        elif left[0] == 'ang' and right[0] == 'val':
            changed |= facts.set_angle_value(ang_key(left[1], left[2], left[3]), right[1])
        elif right[0] == 'ang' and left[0] == 'val':
            changed |= facts.set_angle_value(ang_key(right[1], right[2], right[3]), left[1])
        elif left[0] == 'val' and right[0] == 'val':
            if abs(left[1] - right[1]) > 1e-10:
                raise ValueError("Impossible constraint: angle values differ")
        return changed

# =====================================================================
# Solver & Branch
# =====================================================================

class Solver:
    def __init__(self):
        self.branches = [SolverBranch()]

    def solve(self, stop_condition=None):
        for branch in self.branches:
            branch.solve(stop_condition)

class SolverBranch:
    def __init__(self):
        self.symbols = {}
        self.constraints = []
        self.facts = Facts()
        self.rules = [LengthEqualityRule(), AngleEqualityRule()]

    def add_symbol(self, obj):
        if getattr(obj, "name", None) and obj.name not in self.symbols:
            self.symbols[obj.name] = obj

    def add_constraint(self, c):
        self.constraints.append(c)

    def get_segment_value(self, a, b):
        return self.facts.get_segment_value(seg_key(a, b))

    def get_angle_value(self, a, b, c):
        return self.facts.get_angle_value(ang_key(a, b, c))

    def solve(self, stop_condition=None):
        agenda = list(range(len(self.constraints)))
        while agenda:
            idx = agenda.pop()
            cons = self.constraints[idx]
            for rule in self.rules:
                if cons[0] == rule.kind:
                    changed = rule.apply(cons, self.facts)
                    if changed:
                        agenda.extend(range(len(self.constraints)))  # recheck all
            if stop_condition and stop_condition(self):
                return