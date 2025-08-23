from .geometry import *

# =====================================================================
# DSU: Data structure for handling set of equalities
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
# Facts store: keeps equalities + assigns numeric values
# =====================================================================
class Facts:
    def __init__(self):
        self.seg_dsu = DSU()
        self.ang_dsu = DSU()
        self.seg_val = {}  # rep -> value
        self.ang_val = {}
        self.triangles = {}

    # --- Segments ---
    def merge_segments(self, s1, s2):
        r1, r2 = self.seg_dsu.find(s1), self.seg_dsu.find(s2)
        changed_objects = []
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
    
    def get_value(self, t):
        if isinstance(t, Angle):
            return self.get_angle_value(t)
        elif isinstance(t, Line):
            return self.get_segment_value(t)
        else:
            raise


# =====================================================================
# Rules: the backbone rules of geometry
# =====================================================================
class GeometricRule:
    kind : str
    
    def apply(self, cons, facts):
        raise NotImplementedError

# AB == ?
class LineLengthRule(GeometricRule):
    kind = "Line == Number"
    def apply(self, cons, facts: Facts):
        L, R = cons.out()
        changed = facts.set_segment_value(L, R.value)
        return facts.seg_dsu.find(L) if changed else None

# <ABC == 30
class AngleValueRule(GeometricRule):
    kind = "Angle == Number"
    def apply(self, cons, facts: Facts):
        L, R = cons.out()
        changed = facts.set_angle_value(L, R.value)
        return facts.ang_dsu.find(L) if changed else None

# AB == CD
class LineEqualityRule(GeometricRule):
    kind = "Line == Line"
    def apply(self, cons, facts):
        L, R, = cons.out()
        changed = facts.merge_segments(L, R)
        return facts.seg_dsu.find(L) if changed else None
    
class AngleEqualityRule(GeometricRule):
    kind = "Angle == Angle"
    def apply(self, cons, facts):
        L, R = cons.out()
        changed = facts.merge_angles(L, R)
        return facts.ang_dsu.find(L) if changed else None
    
class IsoscelesAnglesRule(GeometricRule):
    kind = "Angle"
    def apply(self, changed_angle, facts: Facts):
        changed_segments = []

        triangles = [tri for tri in facts.triangles.values() if set(changed_angle.points) <= frozenset(tri.points)]

        for tri in triangles:
            for vertex in tri.points:
                if vertex == changed_angle.vertex:
                    continue
                
                
                if facts.ang_dsu.find(changed_angle) == facts.ang_dsu.find(tri.angles[vertex]):

                    side1 = tri.sides[changed_angle.vertex]
                    side2 = tri.sides[vertex]
                    try:
                        if facts.merge_segments(side1, side2):
                            changed_segments.append(facts.seg_dsu.find(side1))
                    except ValueError:
                        raise ValueError("Impossible constraint: Isosceles rule conflict")
        return changed_segments


    

