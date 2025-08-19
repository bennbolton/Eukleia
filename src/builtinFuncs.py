from geometry import *
from AST import *
import math


def make_circle(*args):
    # Circle(x, y, r)
    if len(args) == 3 and all(isinstance(a, NumberNode) for a in args):
        x, y, r = args
        return Circle(center=Point(x, y), radius=r)
    
    # Circle(O, r)
    elif len(args) == 2 and isinstance(args[0], Point) and isinstance(args[1], (int, float, UnknownNode)):
        center, r = args
        return Circle(center=center, radius=r)
    
    elif len(args) >= 3 and all(isinstance(a, Point) for a in args):
        return Circle(points=args)
    
    else:
        raise TypeError("Unknown argument arrangement for Circle()")

def make_point(*args):
    if len(args) == 1 and isinstance(args[0], tuple):
        return Point(args[0][0], args[0][1])
    elif len(args) == 2 and all(isinstance(a, NumberNode) for a in args):
        return Point(args[0], args[1])
    else:
        raise TypeError("Unknown argument arrangement for Point()")
    
def make_line(*args):
    if all(isinstance(a, Point) for a in args):
        return Line(points=args)
    
def make_angle(*args):
    if len(args) == 3 and all(isinstance(a, Point) for a in args):
        return Angle(points=args).value

def get_type(*args):
    if len(args) == 1:
        return type(args[0]).name
    else:
        raise TypeError(f"Type only takes 1 positional argument, got {len(args)}")
    

def printout(*args):
    if len(args) == 1:
        blue = '\033[94m'
        end = '\033[0m'
        print(f"{blue}{args[0]}{end}")
    else:
        raise TypeError(f"Type only takes 1 positional argument, got {len(args)}")

def rad2deg(*args):
    if len(args) == 1 and isinstance(args[0], NumberNode):
        return NumberNode(math.degrees(args[0].value))
    else:
        raise TypeError(f"Deg only takes 1 positional argument of type NumberNode, got {len(args)}")
    
def deg2rad(*args):
    if len(args) == 1 and isinstance(args[0], NumberNode):
        return NumberNode(math.radians(args[0].value))
    else:
        raise TypeError(f"Rad only takes 1 positional argument of type NumberNode, got {len(args)}")
    

BUILTINS = {
    "Circle": make_circle,
    "Angle": make_angle,
    "Point": make_point,
    "Type": get_type,
    "Print": printout,
    "Line": make_line,
    "Deg": rad2deg,
    "Rad": deg2rad
}