class ASTNode:
    pass

# Expressions
class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(round(self.value, 2))
    
class UnknownNode(NumberNode):
    def __init__(self):
        self.value = '?'
    def __repr__(self):
        return '?'

class VariableReference(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return str(self.name)   
    
class ObjectReference(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return str(self.name)


class ObjectNode(ASTNode):
    def __init__(self, *args):
        self.args = args
        pass
    
    def __repr__(self):
        return f"{type(self).__name__}({', '.join(map(str, self.args))})"
    
class PointNode(ObjectNode):
    pass

class LineNode(ObjectNode):
    pass

class CircleNode(ObjectNode):
    pass

class AngleNode(ObjectNode):
    pass
        
class ObjectDefinition(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f'{type(self).__name__}({self.name}, {self.value})'


class VariableDefinition(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f'{type(self).__name__}({self.name}, {self.value})'
    

class ConstraintNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left        # could be line or length
        self.operator = operator
        self.right = right
    def __repr__(self):
        return f"{type(self).__name__}({self.left}, {self.operator}, {self.right})"
        

class QueryNode(ASTNode):
    def __init__(self, name, function, args):
        self.name = name        # variable to store result
        self.function = function
        self.args = args        # arguments to the function
    def __repr__(self):
        return f'{self.function}({', '.join(map(str, self.args))})'
        
class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    
    def __repr__(self):
        return f"{type(self).__name__}({self.left}, {self.op}, {self.right})"
