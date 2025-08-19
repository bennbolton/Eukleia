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
        # -- Primitives
        if isinstance(node, (NumberNode, Point, Circle, Line)):
            return node
        
        # -- Object/Variable Definitions
        elif isinstance(node, (ObjectDefinition, VariableDefinition)):
            ident = node.ident if (not isinstance(node.ident, ASTNode)) or isinstance(node.ident, (CollectionNode, )) else self.evaluate(node.ident)
            value = node.value if not isinstance(node.ident, ASTNode) or isinstance(node.ident, (CollectionNode, )) else self.evaluate(node.value)
            # Handle Collections
            if isinstance(ident, CollectionNode):
                # Both Collections
                if isinstance(value, CollectionNode):
                    if len(ident) == len(value):
                        for i in range(len(ident)):
                            self.evaluate(ObjectDefinition(ident.items[i], value.items[i]))
                    else:
                        raise ValueError(f"Mismatched Collection Sizes: {len(ident)} and {len(value)}")
                # Collection = value
                else:
                    for i in range(len(ident)):
                        self.evaluate(ObjectDefinition(ident.items[i], value))
            # Obj = Collection
            elif isinstance(value, CollectionNode):
                self.symbols[ident] = Collection(value.items)
            # Stanadrd A = B
            else:
                self.symbols[ident] = value
        
        # -- Object/Variable Reference
        elif isinstance(node, (ObjectReference, VariableReference)):
            value = self.symbols.get(node.name)
            if value is None:
                return node.name
            return self.evaluate(value)
            
            
        elif isinstance(node, PointNode):
            return make_point(*node.args)
        
        elif isinstance(node, CollectionNode):
            pass
        
        elif isinstance(node, CircleNode):
            evaluated_args = []
            for arg in node.args:
                evaluated_args.append(self.evaluate(arg))
            return make_circle(*evaluated_args)
        
        
        elif isinstance(node, QueryNode):
            
            args = [self.evaluate(arg) if isinstance(arg, ASTNode) else arg for arg in node.args]

            # print(f"Query: {node.function}({', '.join(map(str, args))})")
            func = BUILTINS.get(node.function)
            if func:
                return func(*args)
            else:
                raise NameError(f"Unknown function '{node.function}'")

        elif isinstance(node, ConstraintNode):
            self.constraints.append(node)
        else:
            raise ValueError(f"Unknown AST Node type: {type(node)}. Node: {node}")
            