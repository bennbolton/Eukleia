from .geometry import *

def make_number(*args):
    raise

def make_circle(*args):
    # Circle(x, y, r)
    # Circle(O, r)
    raise TypeError("Unknown argument arrangement for Circle()")

def make_point(*args):
    if len(args) == 1 and isinstance(args[0], str):
        return Point(args[0])
    
def make_line(*args):
    if all(isinstance(a, Point) for a in args):
        return Line(points=args)
    
def make_angle(*args, context=None):
    if len(args) == 3 and all(isinstance(a, Point) for a in args):
        AB = make_line(args[:2])
        BC = make_line(args[1:])
        return Angle(lines=[AB, BC])

def get_type(*args, context=None):
    if len(args) == 1:
        return type(args[0]).name
    else:
        raise TypeError(f"Type only takes 1 positional argument, got {len(args)}")
    

# def printout(*args, context=None):
#     blue = '\033[94m'
#     end = '\033[0m'
#     print(f"{blue}{f" ".join([str(arg) for arg in args])}{end}")


def rad2deg(*args, context=None):
    if len(args) == 1 and isinstance(args[0], Number):
        return Number(sp.deg(args[0].value))
    else:
        raise TypeError(f"Deg only takes 1 positional argument of type Number, got {len(args)} of type{'' if len(args) == 1 else 's'}: {', '.join([str(type(arg).__name__) for arg in args])}")
    
def deg2rad(*args, context=None):
    if len(args) == 1 and isinstance(args[0], Number):
        return Number(sp.rad(args[0].value))
    else:
        raise TypeError(f"Rad only takes 1 positional argument of type NumberNode, got {len(args)}")
    

BUILTINFUNCS = {
    "Circle": make_circle,
    "Angle": make_angle,
    "Point": make_point,
    "Type": get_type,
    # "Print": printout,
    "Line": make_line,
    "Deg": rad2deg,
    "Rad": deg2rad,
    "Number": make_number
}