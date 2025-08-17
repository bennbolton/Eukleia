from geometry import *
from AST import *

def make_circle(*args):
    # Circle(x, y, r)
    if len(args) == 3 and all(isinstance(a, Number) for a in args):
        x, y, r = args
        return Circle(center=Point(x, y), radius=r)
    
    # Circle(O, r)
    elif len(args) == 2 and isinstance(args[0], ObjectReference) and isinstance(args[1], (int, float, Unknown)):
        center, r = args
        return Circle(center=center, radius=r)
    
    else:
        raise TypeError("Unknown argument arrangement for Circle()")
        
def get_angle(*args):
    raise Exception
        
BUILTINS = {
    "Circle": make_circle,
    "Angle": get_angle
}