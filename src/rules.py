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
    def apply(self, *args, facts:Facts=None) -> list:
        raise NotImplementedError

# AB == X
class LineLengthRule(GeometricRule):
    kind = "Line == Number"
    def apply(self, cons, facts: Facts):
        L, R = cons.out()
        changed = facts.set_segment_value(L, R.value)
        return [L] if changed else None

# <ABC == X
class AngleValueRule(GeometricRule):
    kind = "Angle == Number"
    def apply(self, cons, facts: Facts):
        L, R = cons.out()
        changed = facts.set_angle_value(L, R.value)
        return [L] if changed else None

# AB == CD
class LineEqualityRule(GeometricRule):
    kind = "Line == Line"
    def apply(self, cons, facts):
        L, R, = cons.out()
        changed = facts.merge_segments(L, R)
        return [L,R] if changed else None

# <ABC == <DEF
class AngleEqualityRule(GeometricRule):
    kind = "Angle == Angle"
    def apply(self, cons, facts):
        L, R = cons.out()
        changed = facts.merge_angles(L, R)
        return [L,R] if changed else None

# if AB == X and BC == X then AB == BC
class LineDefinitionEqualityRule(GeometricRule):
    kind = 'Line'
    def apply(self, changed_line, facts:Facts):
        changed_segments = []
        val1 = facts.get_segment_value(changed_line)
        if val1 is None: return changed_segments
        for other, val2 in facts.seg_val.items():
            if abs(val1 - val2) < 1e-10:
                changed = facts.merge_segments(changed_line, other)
                if changed:
                    changed_segments.extend([changed_line, other])
        return changed_segments
    
# if <ABC == X and <DEF == X then <ABC == <DEF
class AngleDefinitionEqualityRule(GeometricRule):
    kind = 'Angle'
    def apply(self, changed_angle, facts:Facts):
        changed_angles = []
        val1 = facts.get_angle_value(changed_angle)
        if val1 is None: return changed_angles
        for other, val2 in facts.ang_val.items():
            if abs(val1 - val2) < 1e-10:
                changed = facts.merge_angles(changed_angle, other)
                if changed:
                    changed_angles.extend([changed_angle, other])
        return changed_angles

# if <ABC == <BCA then AB == BC
class IsoscelesAngleRule(GeometricRule):
    kind = "Angle"
    def apply(self, changed_angle, facts: Facts):
        changed_segments= []
        triangles = [tri for tri in facts.triangles.values() if set(changed_angle.points) <= frozenset(tri.points)]
        for tri in triangles:
            for i in range(3):
                p1 = tri.points[i]
                p2 = tri.points[(i+1)%3]
                if facts.ang_dsu.find(tri.angles[p1]) == facts.ang_dsu.find(tri.angles[p2]):
                    side1 = tri.sides[p1]
                    side2 = tri.sides[p2]
                    try:
                        if facts.merge_segments(side1, side2):
                            changed_segments.extend([side1, side2])
                    except ValueError:
                        raise ValueError("Impossible constraint: Isosceles rule conflict")
        return changed_segments

# if AB == BC then <ABC == <BCA
class IsoscelesSideRule(GeometricRule):
    kind = "Line"
    def apply(self, changed_angle, facts: Facts):
        changed_angles= []
        triangles = [tri for tri in facts.triangles.values() if set(changed_angle.points) <= frozenset(tri.points)]
        for tri in triangles:
            for i in range(3):
                p1 = tri.points[i]
                p2 = tri.points[(i+1)%3]
                if facts.seg_dsu.find(tri.sides[p1]) == facts.seg_dsu.find(tri.sides[p2]):
                    ang1 = tri.angles[p1]
                    ang2 = tri.angles[p2]
                    try:
                        if facts.merge_angles(ang1, ang2):
                            changed_angles.extend([ang1, ang2])
                    except ValueError:
                        raise ValueError("Impossible constraint: Isosceles rule conflict")
        return changed_angles

# Sum(<ABC, <BCA, <ACB) == 180
class TriangleAngles180Rule(GeometricRule):
    kind = 'Angle'
    def apply(self, changed_angle, facts:Facts):
        changed_angles = []
        triangles = [tri for tri in facts.triangles.values() if set(changed_angle.points) <= frozenset(tri.points)]
        for tri in triangles:
            known_angles, unknown_angles = [], []
            for angle in tri.angles.values():
                (known_angles if facts.get_angle_value(angle) is not None else unknown_angles).append(angle)
            if len(known_angles) == 2 and len(unknown_angles) == 1:
                new_ang = 180 - sum([facts.get_angle_value(ang) for ang in known_angles])
                changed = facts.set_angle_value(unknown_angles[0], new_ang)
                if changed:
                    changed_angles.extend(unknown_angles)
            elif len(known_angles) == 1 and len(unknown_angles) == 2:
                if facts.ang_dsu.find(unknown_angles[0]) == facts.ang_dsu.find(unknown_angles[1]):
                    known_angle = facts.get_angle_value(known_angles[0])
                    other_angles = (180 - known_angle) / 2
                    changed = facts.set_angle_value(unknown_angles[0], other_angles)
                    if changed:
                        changed_angles.extend(unknown_angles)      
        return changed_angles
    
