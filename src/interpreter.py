from AST import *
class Interpreter:
    def __init__(self):
        self.symbols = {}
    
    def run(self, nodes):
        for node in nodes:
            self.evaluate(node)
    
    def evaluate(self, node):
        if isinstance(node, ObjectDefinition):
            value = self.evaluate(node.value) if isinstance(node.value, ASTNode) else node.value
            self.symbols[node.name] = value
            print(f"Defined object {node.name} = {node.value}")
        
        elif isinstance(node, VariableDefinition):
            value = self.evaluate(node.value) if isinstance(node.value, ASTNode) else node.value
            self.symbols[node.name] = value
            print(f"Defined variable {node.name} = {value}")
        
        elif isinstance(node, ObjectReference) or isinstance(node, VariableReference):
            value = self.symbols.get(node.name)
            if value is None:
                raise NameError(f"name: '{node.name}' is not defined")
            return value
        
        elif isinstance(node, Query):
            args = [self.evaluate(arg) if isinstance(arg, ASTNode) else arg for arg in node.args]
            print(f"Query: {node.function}({', '.join(map(str, args))})")
            return None
        
        elif isinstance(node, Number):
            return node.value
        
        elif isinstance(node, Unknown):
            return "?"
        
        else:
            raise ValueError(f"Unknown AST Node type: {node}")
            