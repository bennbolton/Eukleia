import sympy as sp

class EklPrim:
    pass

class Object(EklPrim):
    pass

class Number(EklPrim):
    def __init__(self, value):
        self.value = sp.Rational(value)
    
    def __repr__(self):
        return str(self.value)

class Point(Object):
    def __init__(self, name:str):
        self.name = name

    def __hash__(self):
        return hash(self.name)

class Line(Object):
    def __init__(self, points):
        self._length = None
        if not all(isinstance(point, Point) for point in points): raise ValueError("Invalid Line definition")
        self.points = [points[0], points[-1]]
        self.name = "".join(sorted([p.name for p in self.points]))

    @property
    def length(self):
        return self._length
    
    @length.setter
    def length(self, value):
        if self._length is None:
            self._length = value
        else:
            raise ValueError("Do something idk")
        
    def __str__(self):
        return str(self._length) if self._length is not None else "Undeterminable"
    
    def __repr__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return isinstance(other, Line) and (self.points == other.points or self.points == other.points[::-1])
    

class Angle(Object):
    def __init__(self, points):
        self._value = None
        if len(points) != 3: raise ValueError("Invalid Angle definition")
        self.points = points
        self.lines = [Line(points[:2]), Line(points[1:])]
        rayPoints = sorted([points[0], points[-1]], key=lambda x: x.name)
        self.vertex = points[1]
        self.name = rayPoints[0].name + self.vertex.name + rayPoints[1].name

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if self._value is None:
            self._value = value
        else:
            raise ValueError("Do something idk")
        
    def __str__(self):
        return str(self._value)
    
    def __repr__(self):
        return "<" + self.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return isinstance(other, Angle) and (self.points == other.points or self.points == other.points[::-1])
    
class Triangle(Object):
    def __init__(self, points):
        if len(points) != 3: raise ValueError("Invalid Triangle definition")
        self.points = points
        A,B,C = self.points
        self.sides = {
            C: Line([A,B]),
            B: Line([A,C]),
            A: Line([B,C])
        }
        self.angles = {
            A: Angle([B,A,C]),
            B: Angle([A,B,C]),
            C: Angle([A,C,B])
        }

class Constraint(EklPrim):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def out(self):
        return (self.left, self.right)
    
    def __repr__(self):
        return f"{repr(self.left)} {self.op} {repr(self.right)}"
    
    def consType(self):
        return f"{type(self.left).__name__} {self.op} {type(self.right).__name__}"
    
