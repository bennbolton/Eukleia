class ASTNode:
    pass

class ObjectDefinition(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f'{self.name} = {self.value}'
    
class ObjectReference(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return str(self.name)

class VariableDefinition(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f'{self.name} = {self.value}'
    
class VariableReference(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return str(self.name)   

class Constraint(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left        # could be line or length
        self.operator = operator
        self.right = right

class Query(ASTNode):
    def __init__(self, name, function, args):
        self.name = name        # variable to store result
        self.function = function
        self.args = args        # arguments to the function
    def __repr__(self):
        return f'{self.function}({', '.join(map(str, self.args))})'
        
    
class Number(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(round(self.value, 2))
    
class Unknown(Number):
    def __init__(self):
        self.value = '?'
    def __repr__(self):
        return '?'