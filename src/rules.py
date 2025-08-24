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
        self.parallel_dsu = DSU()
        self.seg_val = {}  # rep -> value
        self.ang_val = {}
        self.triangles = {}

    def _merge_generic(self, x1, x2, dsu, values):
        r1, r2 = dsu.find(x1), dsu.find(x2)
        changed_objects = []
        if r1 == r2:
            return False
        v1, v2 = values.get(r1), values.get(r2)
        r = dsu.union(r1, r2)
        if v1 is not None and v2 is not None and abs(v1 - v2) > 1e-10:
            raise ValueError(f"Impossible constraint: {x1} or {x2} values conflinct")
        if v1 is not None:
            values[r] = v1
        if v2 is not None:
            values[r] = v2
        return True
    
    def _set_value_generic(self, x, dsu, values, val):
        r = dsu.find(x)
        v = values.get(r)
        if v is None:
            values[r] = val
            return True
        if abs(v - val) > 1e-10:
            raise ValueError(f"Impossible constraint: {x} already has different value")
        return False
    
    def get_value(self, t):
        if isinstance(t, Angle):
            return self.get_angle_value(t)
        elif isinstance(t, Line):
            return self.get_segment_value(t)
        else:
            raise

    # --- Segments ---
    def merge_segments(self, s1, s2):
        return self._merge_generic(s1, s2, self.seg_dsu, self.seg_val)

    def set_segment_value(self, s, val):
        return self._set_value_generic(s, self.seg_dsu, self.seg_val, val)

    def get_segment_value(self, s):
        return self.seg_val.get(self.seg_dsu.find(s))

    # --- Angles ---
    def merge_angles(self, a1, a2):
        return self._merge_generic(a1, a2, self.ang_dsu, self.ang_val)

    def set_angle_value(self, a, deg):
        return self._set_value_generic(a, self.ang_dsu, self.ang_val, deg)

    def get_angle_value(self, a):
        return self.ang_val.get(self.ang_dsu.find(a))
    
    # --- Parallels ---
    def merge_parallels(self, s1, s2):
        return self._merge_generic(s1, s2, self.parallel_dsu, {})


# =====================================================================
# Rules: the backbone rules of geometry
# =====================================================================
# --- Definition Rules ---
class DefinitionRule:
    kind : str
    def apply(self, constraint, facts:Facts):
        raise NotImplementedError

# AB == X
class LineLengthDefintion(DefinitionRule):
    kind = "Line == Number"
    def apply(self, cons, facts: Facts):
        L, R = cons.out()
        changed = facts.set_segment_value(L, R.value)
        return [L] if changed else None

# <ABC == X
class AngleValueDefintion(DefinitionRule):
    kind = "Angle == Number"
    def apply(self, cons, facts: Facts):
        L, R = cons.out()
        changed = facts.set_angle_value(L, R.value)
        return [L] if changed else None

# AB == CD
class LineEqualityDefinition(DefinitionRule):
    kind = "Line == Line"
    def apply(self, cons, facts):
        L, R, = cons.out()
        changed = facts.merge_segments(L, R)
        return [L,R] if changed else None

# <ABC == <DEF
class AngleEqualityDefinition(DefinitionRule):
    kind = "Angle == Angle"
    def apply(self, cons, facts):
        L, R = cons.out()
        changed = facts.merge_angles(L, R)
        return [L,R] if changed else None

# AB // CD
class LineParallelDefinition(DefinitionRule):
    kind = "Line // Line"
    def apply(self, cons, facts:Facts):
        L, R = cons.out()
        changed = facts.merge_parallels(L, R)
        return [L,R] if changed else None

# --- Geometric Rules ---
class GeometricRule:
    kind : str
    def apply(self, *args, facts:Facts=None) -> list:
        raise NotImplementedError
    def getTriangles(self, obj, facts):
        return [tri for tri in facts.triangles.values() if set(obj.points) <= frozenset(tri.points)]
    
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
    def apply(self, value, facts: Facts):
        changed_segments= []
        for tri in self.getTriangles(value, facts):
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
    def apply(self, value, facts: Facts):
        changed_angles= []
        for tri in self.getTriangles(value, facts):
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

# class ParallelCorrespondingAnglesRule(GeometricRule):
#     kind = "Angle"
#     def apply(self, angle, facts:Facts):
#         for line1 in angle.lines:
#             for line2 in facts.parallel_dsu.parent:
#                 if facts.parallel_dsu.find(line1) == facts.parallel_dsu.find(line2):

# a/sin(A) = b/sin(B) = c/sin(C)
class TriangleSinRule(GeometricRule):
    kind = "Angle or Line"
    def apply(self, value, facts:Facts):
        changed_values = []
        for tri in self.getTriangles(value, facts):
            for p1 in tri.points:
                ang1 = facts.get_angle_value(tri.angles[p1])
                side1 = facts.get_segment_value(tri.sides[p1])
                if ang1 is not None and side1 is not None:
                    for p2 in tri.points:
                        if p1 == p2:
                            continue
                        ang2 = facts.get_angle_value(tri.angles[p2])
                        side2 = facts.get_segment_value(tri.sides[p2])
                        if ang2 is not None and side2 is None:
                            val = sp.sin(sp.rad(ang2)) * side1 / sp.sin(sp.rad(ang1))
                            if facts.set_segment_value(tri.sides[p2], val):
                                changed_values.append(side2)
                        elif ang2 is None and side2 is not None:
                            val = sp.deg(sp.asin(side2 * sp.sin(sp.rad(ang1)) / side1))
                            if facts.set_angle_value(tri.angles[p2], val):
                                changed_values.append(ang2)
        return changed_values

# a^2 = b^2 + c^2 -2*b*c*cos(A)
class TriangleCosineRule(GeometricRule):
    kind = "Angle or Line"
    def apply(self, value, facts:Facts):
        changed_values = []
        for tri in self.getTriangles(value, facts):
            sides = {point: facts.get_segment_value(tri.sides[point]) for point in tri.points}
            angles = {point: facts.get_angle_value(tri.angles[point]) for point in tri.points}

            # Unknown side
            for p1, length in sides.items():
                if length is None:
                    other_sides = [val for p, val in sides.items() if p != p1 and val is not None]
                    if len(other_sides) == 2 and angles[p1] is not None:
                        s1, s2 = other_sides
                        val = sp.sqrt(s1**2 + s2**2 - 2*s1*s2*sp.cos(sp.rad(angles[p1])))
                        if facts.set_segment_value(tri.sides[p1], val):
                            changed_values.append(tri.sides[p1])
                elif all(sides.values()):
                    s1, s2 = [val for p, val in sides.items() if p != p1 and val is not None]
                    val = sp.deg(sp.acos((s1**2 + s2**2 - sides[p1]**2) / (2*s1*s2)))
                    if facts.set_angle_value(tri.angles[p1], val):
                        changed_values.append(tri.angles[p1])
        return changed_values

