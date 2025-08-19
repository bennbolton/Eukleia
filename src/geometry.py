from helperFuncs import *

class Object:
    pass

class Number(Object):
    def __init__(self, value):
        self.value = value
        
    def __add__(self, other):
        if isinstance(other, Number):
            return self.value + other.value
        else:
            return self.value + other
        
    def __repr__(self):
        return str(self.value)
        
class Unknown(Number):
    def __init__(self):
        self.value = '?'
    
    def __repr__(self):
        return '?'

class Point(Object):
    name = "Point"
    def __init__(self, x='?', y='y'):
        self.x = x
        self.y = y
        
        self.defined = self.isDefined()
        
    def isDefined(self):   
        return all(isinstance(a, (float, int)) for a in [self.x, self.y])
    
    def __repr__(self):
        return f"({self.x}, {self.y})"
    

class Line(Object):
    name = "Line"
    def __init__(self, *, points=None, grad=None):
        self.grad = grad
        self.points = points
        
        self.evaluate()
        self.defined = self.isDefined()
        
    def isDefined(self):
        if any(a.isDefined() for a in self.points) and (self.grad):
            return True
        elif self.points and len(self.points) >=1 and len(list(filter(lambda x: x.isDefined(), self.points))) >=2:
            return True
        else:
            return False
        
    def evaluate(self):
        if self.points:
            if not are_points_colinear(self.points): raise ValueError(f"Points are not all colinear")
            definedPoints = list(filter(lambda x: x.isDefined(), self.points))
            if len(definedPoints) >= 2:
                p1, p2 = definedPoints[0], definedPoints[1]
                if (p2.x - p1.x) != 0:
                    self.grad = (p2.y - p1.y) / (p2.x - p1.x)
                else:
                    self.grad = float('inf')
            else:
                pass #grad and point check later
    
    def pointOnLine(self, point):
        """
        Returns True if the given point lies on the line, False otherwise.
        Uses a small tolerance for floating-point comparison.
        """
        tol = 1e-9
        # The line can be defined by two points or by a gradient and a point
        if self.points and len(self.points) >= 2:
            p1, p2 = self.points[0], self.points[1]
            if p1.isDefined() and p2.isDefined() and point.isDefined():
                # Handle vertical line
                if abs(p2.x - p1.x) < tol:
                    return abs(point.x - p1.x) < tol
                else:
                    # Line equation: (y - y1) = m*(x - x1)
                    m = (p2.y - p1.y) / (p2.x - p1.x)
                    expected_y = m * (point.x - p1.x) + p1.y
                    return abs(point.y - expected_y) < tol
        elif self.grad is not None and self.points and len(self.points) >= 1:
            # Use gradient and a known point
            p0 = self.points[0]
            if p0.isDefined() and point.isDefined():
                if abs(self.grad) == float('inf'):
                    return abs(point.x - p0.x) < tol
                else:
                    expected_y = self.grad * (point.x - p0.x) + p0.y
                    return abs(point.y - expected_y) < tol
        return False
    

        

class Angle(Object):
    name = "Angle"
    def __init__(self, points=None, lines=None):
        self.points = points
        self.lines = lines
        
        self.defined = self.isDefined()
        self.value = self.calc()
        
        
    def isDefined(self):
        if self.lines and len(self.lines) == 2 and all(getattr(l, 'grad') for l in self.lines):
            return True
        elif self.points and len(self.points) == 3 and all(p and p.isDefined() for p in self.points):
            return True
        else:
            return False
        
    def calc(self):
        if not self.isDefined():
            return self
        
        elif self.points and len(self.points) == 3 and self.isDefined():
            return angle_from_three_points(self.points[0], self.points[1], self.points[2])

        
        

class Circle(Object):
    name = "Circle"
    def __init__(self, *, center=None, radius=None, points=None):
        self.center = center
        self.radius = radius
        
        self.points = points
        self.evaluate()
        
        self.defined = self.isDefined()
        
    def isDefined(self):
        if self.center is not None and self.radius is not None:
            return True
        elif len(self.points) >= 3 and len(list(filter(lambda x: x.isDefined(), self.points))) >= 3:
            return True
        else:
            return False
        
    def evaluate(self):
        if self.points and len(self.points) >= 3:
            definedPoints = list(filter(lambda x: x.isDefined(), self.points))
            if self.center is None and self.radius is None and len(definedPoints) >= 3:
                cx, cy, r = circle_from_three_points(definedPoints[0], definedPoints[1], definedPoints[2])
                self.center = Point(cx, cy)
                self.radius = r
        self.defined = self.isDefined()
    
    def __repr__(self):
        if self.defined:
            return f"Circle with center {self.center} and radius {self.radius}"
        else:
            return f"Undefined Circle..."

class Collection(Object):
    def __init__(self, items):
        self.items = items
        