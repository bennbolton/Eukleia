from .helperFuncs import *
import sympy as sp
from uuid import uuid4

class EklPrim:
    pass

class Object(EklPrim):
    pass

class Number(Object):
    unknownCount = 0
    def __init__(self, value):
        if value is None:
            self.value = sp.Symbol('?' + str(self.unknownCount), real=True)
            Number.unknownCount += 1
        else:
            self.value = value if isinstance(value, sp.Expr) else sp.Rational(value)
    
    def as_sympy(self):
        if isinstance(self.value, sp.Expr):
            return self.value
        else:
            raise TypeError("Idk man")
        
    def isDefined(self):
        return not self.value.has(sp.Symbol)
        
    def __add__(self, other):
        if isinstance(other, Number):
            return self.value + other.value
        else:
            return self.value + other
        
    def __sub__(self, other):
        if isinstance(other, Number):
            return self.value - other.value
        else:
            return self.value - other
        
    def __mul__(self, other):
        if isinstance(other, Number):
            return self.value * other.value
        else:
            return self.value * other
        
    def __truediv__(self, other):
        if isinstance(other, Number):
            return self.value / other.value
        else:
            return self.value / other
        
    def symbols(self):
        return self.value.free_symbols
    
    def substitute(self, solution):
        self.value = sp.simplify(self.value.subs(solution))

    def __repr__(self):
        val = self.value
        return sp.sstr(val)
    
    def __eq__(self, other):
        if isinstance(other, Number):
            return self.value == other.value

class Point(Object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        # self.defined = self.isDefined()
        
    # def isDefined(self):   
    #     return all(isinstance(a, (float, int)) for a in [self.x, self.y])
    
    def as_tuple(self):
        return (self.x, self.y)
    
    def symbols(self):
        return self.x.symbols() | self.y.symbols()
    
    def substitute(self, solution):
        self.x.substitute(solution)
        self.y.substitute(solution)

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
    
    
    def __repr__(self):
        return f"({self.x}, {self.y})"
    

class Line(Object):
    def __init__(self, *, points=None):
        self.points = points
        if len(self.points) == 2:
            self.A = self.points[0]
            self.B = self.points[1]
        else:
            # Can be changed later if needs be
            self.A = None
            self.B = None
        
        # self.evaluate()
        # self.defined = self.isDefined()
        
    # def isDefined(self):
    #     if any(a.isDefined() for a in self.points) and (self.grad):
    #         return True
    #     elif self.points and len(self.points) >=1 and len(list(filter(lambda x: x.isDefined(), self.points))) >=2:
    #         return True
    #     else:
    #         return False
        
    def substitute(self, solution):
        for point in self.points:
            point.substitute(solution)
        
    # def evaluate(self):
    #     if self.points:
    #         if not are_points_colinear(self.points): raise ValueError(f"Points are not all colinear")
    #         definedPoints = list(filter(lambda x: x.isDefined(), self.points))
    #         if len(definedPoints) >= 2:
    #             p1, p2 = definedPoints[0], definedPoints[1]
    #             if (p2.x - p1.x) != 0:
    #                 self.grad = (p2.y - p1.y) / (p2.x - p1.x)
    #             else:
    #                 self.grad = float('inf')
    #         else:
    #             pass #grad and point check later

    def as_implicit(self):
        """Return the implicit line equation: ax + by + c = 0"""
        x, y = sp.symbols("x y")
        x1, y1 = self.A.x.as_sympy(), self.A.y.as_sympy()
        x2, y2 = self.B.x.as_sympy(), self.B.y.as_sympy()
        return (y2 - y1) * (x - x1) - (x2 - x1) * (y - y1)
    
    def as_parametric(self):
        """Return parametric form (x(t), y(t))"""
        t = sp.symbols("t")
        x1, y1 = self.A.x.as_sympy(), self.A.y.as_sympy()
        x2, y2 = self.B.x.as_sympy(), self.B.y.as_sympy()
        return (x1 + t*(x2 - x1), y1 + t*(y2 - y1))

    def direction(self):
        """Return direction vector (dx, dy)"""
        x1, y1 = self.A.x.as_sympy(), self.A.y.as_sympy()
        x2, y2 = self.B.x.as_sympy(), self.B.y.as_sympy()
        return (x2 - x1, y2 - y1)
    
    def length_squared(self):
        # This is a bad method, needs updating to be safer
        if len(self.points) == 2:
            return (self.B.x.value - self.A.x.value)**2 + (self.B.y.value - self.A.y.value)**2
        
    def length(self):
       return sp.sqrt(self.length_squared())

    def symbols(self):
        syms = set()
        for point in self.points:
            syms |= point.symbols()
        return list(syms)
    
    def gradient(self):
        direction = self.direction()
        return direction[1] / direction[0]

    
    def __repr__(self):
        return str(self.length())
    
    def __eq__(self, other):
        # Not technically correct, needs some sort of offset too
        return self.direction() == other.direction()
        

class Angle(Object):
    def __init__(self, points=None):
        self.points = points
        
        
    def as_sympy(self):        
        # atan2(cross, dot) now gives correct oriented angle
        return sp.atan2(self.cross(), self.dot())
    
    def cross(self):
        if len(self.points) == 3:
            BAx = self.points[0].x.value - self.points[1].x.value
            BAy = self.points[0].y.value - self.points[1].y.value
            BCx = self.points[2].x.value - self.points[1].x.value
            BCy = self.points[2].y.value - self.points[1].y.value
            return BAx*BCy - BAy*BCx
    
    def dot(self):
        if len(self.points) == 3:
            BAx = self.points[0].x.value - self.points[1].x.value
            BAy = self.points[0].y.value - self.points[1].y.value
            BCx = self.points[2].x.value - self.points[1].x.value
            BCy = self.points[2].y.value - self.points[1].y.value
            
            return BAx*BCx + BAy*BCy
    
    def cos(self):
        return self.dot() / self.norm()
            
    def norm(self):
        if len(self.points) == 3:
            BAx = self.points[0].x.value - self.points[1].x.value
            BAy = self.points[0].y.value - self.points[1].y.value
            BCx = self.points[2].x.value - self.points[1].x.value
            BCy = self.points[2].y.value - self.points[1].y.value
            
            return sp.sqrt(BAx**2 + BAy**2) * sp.sqrt(BCx**2 + BCy**2)
    
    def sin(self):
        return self.cross() / self.norm()
        
    def substitute(self, solution):
        for point in self.points:
            point.substitute(solution)
        
    def __repr__(self):
        return str(self.as_sympy())
    
    def __eq__(self, other):
        if isinstance(other, Angle):
            return sp.simplify(sp.And(sp.Eq(self.cos(), other.cos()), 
                          sp.Eq(self.sin(), other.sin())))
        elif isinstance(other, Number):
            return sp.simplify(sp.And(sp.Eq(self.cos(), sp.cos(other.as_sympy())), 
                          sp.Eq(self.sin(), sp.sin(other.as_sympy()))))
        # return sp.simplify(self.as_sympy() - other.as_sympy()) == 0

        
class Circle(Object):
    def __init__(self, *, center=None, radius=None, points=None):
        self.center = center
        self.radius = radius
        
        self.points = points
        # self.evaluate()
        
    #     self.defined = self.isDefined()
        
    # def isDefined(self):
    #     if self.center is not None and self.radius is not None:
    #         return True
    #     elif len(self.points) >= 3 and len(list(filter(lambda x: x.isDefined(), self.points))) >= 3:
    #         return True
    #     else:
    #         return False
        
    # def evaluate(self):
    #     if self.points and len(self.points) >= 3:
    #         definedPoints = list(filter(lambda x: x.isDefined(), self.points))
    #         if self.center is None and self.radius is None and len(definedPoints) >= 3:
    #             cx, cy, r = circle_from_three_points(definedPoints[0], definedPoints[1], definedPoints[2])
    #             self.center = Point(cx, cy)
    #             self.radius = r
    #     self.defined = self.isDefined()
    
    # def __repr__(self):
    #     if self.defined:
    #         return f"Circle with center {self.center} and radius {self.radius}"
    #     else:
    #         return f"Undefined Circle..."


class Constraint(EklPrim):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        
    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"


class Collection(EklPrim):
    def __init__(self, items):
        self.items = items
        

# ------
# class BranchReference:
#     def __init__(self, name, solution_set):
#         self.name = name
#         self.solution_set = solution_set

#     def get_values(self):
#         return [solver.symbols.get(self.name) for solver in self.solution_set.solvers]
    
    # def __repr__(self):
    #     return f"({(str(self.get_values()))})"