from .geometry import *


def make_number(*args, context=None):
    # Number
    if len(args) == 1 and isinstance(args[0], (int, float)):
        return Number(args[0])
    # Unknown or inf
    elif len(args) == 1 and args[0] is None:
        return Number(None)
    elif args[0] == 'inf':
        return Number(args[0])


def make_circle(*args, context=None):
    # Circle(x, y, r)
    if len(args) == 3 and all(isinstance(a, Number) for a in args):
        x, y, r = args
        return Circle(center=Point(x, y), radius=r)
    
    # Circle(O, r)
    elif len(args) == 2 and isinstance(args[0], Point) and isinstance(args[1], Number):
        center, r = args
        return Circle(center=center, radius=r.value)
    
    elif len(args) >= 3 and all(isinstance(a, Point) for a in args):
        return Circle(points=args)
    
    else:
        raise TypeError("Unknown argument arrangement for Circle()")

def make_point(*args, context=None):
    if len(args) == 1 and isinstance(args[0], tuple):
        return Point(args[0][0], args[0][1])
    elif len(args) == 2 and all(isinstance(a, Number) for a in args):
        return Point(args[0], args[1])
    else:
        raise TypeError("Unknown argument arrangement for Point()")
    
def make_line(*args, context=None):

    # print([type(a) for a in args])
    if all(isinstance(a, Point) for a in args):
        return Line(points=args)
    
def make_angle(*args, context=None):
    if len(args) == 3 and all(isinstance(a, Point) for a in args):
        return Angle(points=args)
    # elif len(args) == 3 and all(isinstance(a, str) for a in args):
    #     return Angle(points=)

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