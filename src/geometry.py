from helperFuncs import *

class Object:
    pass

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
        
        self.defined = self.isDefined()
        
    def isDefined(self):
        if any(a.isDefined() for a in self.points) and (self.grad):
            return True
        elif self.points and len(self.points) >=1 and len(list(filter(lambda x: x.isDefined(), self.points))) >=2:
            return True
        else:
            return False
        

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

