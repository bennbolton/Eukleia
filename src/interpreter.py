from AST import *
from builtinFuncs import *
class Interpreter:
    def __init__(self):
        self.symbols = {}
        self.constraints = []
        
    
    def run(self, nodes):
        for node in nodes:
            self.evaluate(node)
            
    
    def evaluate(self, node):
        if isinstance(node, Number):
            return node
        
        elif isinstance(node, tuple):
            return BUILTINS.get("Point")(node)
        
        elif isinstance(node, Object):
            return node
        
        elif isinstance(node, ObjectDefinition):
            value = self.evaluate(node.value) if isinstance(node.value, ASTNode) else node.value
            self.symbols[node.name] = value
            # print(f"Defined object {node.name} = {node.value}")
        
        elif isinstance(node, VariableDefinition):
            if isinstance(node.value, Number):
                self.symbols[node.name] = node.value
                # print(f"Defined variable {node.name} = {node.value}")
            else:
                value = self.evaluate(node.value)
                if isinstance(value, Object):
                    raise NameError(f"Variables cannot be Objects")
                self.symbols[node.name] = value
            
        
        elif isinstance(node, (ObjectReference, VariableReference)):
            value = self.symbols.get(node.name)
            if value is None:
                raise NameError(f"name: '{node.name}' is not defined")
            return self.evaluate(value)
        
        elif isinstance(node, Query):
            
            args = [self.evaluate(arg) if isinstance(arg, ASTNode) else arg for arg in node.args]

            # print(f"Query: {node.function}({', '.join(map(str, args))})")
            func = BUILTINS.get(node.function)
            if func:
                return func(*args)
            else:
                raise NameError(f"Unknown function '{node.function}'")

        elif isinstance(node, Constraint):
            self.constraints.append(node)
        else:
            raise ValueError(f"Unknown AST Node type: {type(node)}. Node: {node}")
            