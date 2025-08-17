class Object:
    pass

class Circle(Object):
    def __init__(self, *, center=None, radius=None, points=None):
        self.center = center
        self.radius = radius
        
        self.points = points
        
        self.defined = self.isDefined()
        
    def isDefined(self):
        if self.center is not None and self.radius is not None:
            return True
        elif len(self.points) >= 3 and len(filter(lambda x: x.isDefined(), self.points)) >= 3:
            return True
        else:
            return False
        
    def evaluate(self):
        pass
    
    def __repr__(self):
        return f"Circle with center {self.center} and radius {self.radius}"

class Point(Object):
    def __init__(self, x='?', y='y'):
        self.x = x
        self.y = y
        
        self.defined = self.isDefined()
        
    def isDefined(self):   
        return all(isinstance(a, (float, int)) for a in [self.x, self.y])
    
    def __repr__(self):
        return f"({self.x}, {self.y})"