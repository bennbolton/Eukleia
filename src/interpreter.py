from AST import *
from builtinFuncs import *
class Interpreter:
    
    BINARY_OPS = {
        '+': lambda a,b: Number(a + b),
        '-': lambda a,b: Number(a - b),
        '*': lambda a,b: Number(a * b),
        '/': lambda a,b: Number(a / b),
    }
    def __init__(self):
        self.symbols = {}
        self.constraints = []
        
    
    def run(self, nodes):
        for node in nodes:
            self.evaluate(node)
            
    
    def evaluate(self, node):
        
        # -- Primitives
        if isinstance(node, (Number, Point, Circle, Line)):
            return node
        
        # -- Numbers
        elif isinstance(node, NumberNode):
            return type(node).func(node.value)
        
        # -- Object/Variable Definitions
        elif isinstance(node, (ObjectDefinition, VariableDefinition)):
            # ident = node.ident if (not isinstance(node.ident, ASTNode)) or isinstance(node.ident, (CollectionNode, )) else self.evaluate(node.ident)
            # value = node.value if not isinstance(node.ident, ASTNode) or isinstance(node.ident, (CollectionNode, )) else self.evaluate(node.value)
            ident = self.evaluate(node.ident)
            value = self.evaluate(node.value)
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
                self.symbols[node.name] = Point(ident = node.name)
                return self.symbols[node.name]
            return self.evaluate(value)
           
        # -- Keywords 
        elif isinstance(node, (PointNode, CircleNode, LineNode, AngleNode)):
            evaluated_args = []
            for arg in node.args:
                evaluated_args.append(self.evaluate(arg))
            return type(node).func(*evaluated_args, ident=node.name)
        
        elif isinstance(node, BinaryOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            op = node.op
            return self.BINARY_OPS[op](left, right)
                
        
        # -- Collections
        elif isinstance(node, CollectionNode):
            pass
    
        # -- Constraints
        elif isinstance(node, ConstraintNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            self.constraints.append(Constraint(left, node.operator, right))
        
        
        else:
            raise ValueError(f"Unknown AST Node type: {type(node)}. Node: {node}")
            