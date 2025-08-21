from .builtinFuncs import *

class ASTNode:
    def __init__(self, *args):
        self.args = args

# Expressions
class NumberNode(ASTNode):
    func = make_number
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"{type(self).__name__}({self.value if self.value is not None else '?'})"
    

class VariableReference(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"{type(self).__name__}({self.name})" 
    
class ObjectReference(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"{type(self).__name__}({self.name})"
    def __str__(self):
        return self.name


class ObjectNode(ASTNode):
    def __init__(self, *args, name=None):
        self.name = name
        self.args = args
        pass
    
    def __repr__(self):
        return f"{type(self).__name__}({', '.join(map(str, self.args))})"
    
class PointNode(ObjectNode):
    func = make_point
    pass

class LineNode(ObjectNode):
    func = make_line

    def __str__(self):
        label = ""
        for point in self.args:
            label += str(point)
        return label


class CircleNode(ObjectNode):
    func = make_circle
    pass

class AngleNode(ObjectNode):
    func = make_angle
    
    def __str__(self):
        label = "<"
        for point in self.args:
            label += str(point)
        return label
        
class ObjectDefinition(ASTNode):
    def __init__(self, ident, value):
        self.ident = ident
        self.value = value
    def __repr__(self):
        return f'{type(self).__name__}({self.ident}, {self.value})'


class VariableDefinition(ASTNode):
    def __init__(self, ident, value):
        self.ident = ident
        self.value = value
    def __repr__(self):
        return f'{type(self).__name__}({self.ident}, {self.value})'
    

class ConstraintNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left        # could be line or length
        self.operator = operator
        self.right = right
    def __repr__(self):
        return f"{type(self).__name__}({self.left}, {self.operator}, {self.right})"
        

class QueryNode(ASTNode):
    def __init__(self, function, args):
        self.func = function
        self.args = args        # arguments to the function
    def __repr__(self):
        return f'{self.func}({', '.join(map(str, self.args))})'
        
class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    
    def __repr__(self):
        return f"{type(self).__name__}({self.left}, {self.op}, {self.right})"
    
class CollectionNode(ASTNode):
    def __init__(self, items: list):
        self.items = items
    
    def __len__(self):
        return len(self.items)
        
    def __repr__(self):
        return f"{type(self).__name__}({', '.join(map(str, self.items))})"
    
class NotNode(ASTNode):
    def __init__(self, inner):
        self.inner = inner

    def __repr__(self):
        return f"{type(self).__name__}({str(self.inner)})"
    
class PrintNode(ASTNode):
    # func = printout
    def __init__(self, *args):
        self.args = args
