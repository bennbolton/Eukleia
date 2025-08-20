from .astNodes import *
from .builtinFuncs import *
from .solver import Solver, SolutionSet
    
class Interpreter:
    
    BINARY_OPS = {
        '+': lambda a,b: Number(a + b),
        '-': lambda a,b: Number(a - b),
        '*': lambda a,b: Number(a * b),
        '/': lambda a,b: Number(a / b),
    }
    def __init__(self, solver):
        self.solver = solver
        self.solution_set = SolutionSet()
        pass
        
    
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
                    self.evaluate(ObjectDefinition(ident.items[0], value))
                    for i in range(len(ident)-1):
                        fresh_value = self.evaluate(node.value)
                        self.evaluate(ObjectDefinition(ident.items[i+1], fresh_value))
            # Obj = Collection
            elif isinstance(value, CollectionNode):
                self.solution_set.add_object(ident, Collection(value.items))
            # Stanadrd A = B
            else:
                self.solution_set.add_object(ident.name, value)
        
        # -- Object/Variable Reference
        elif isinstance(node, (ObjectReference, VariableReference)):
            return self.solution_set.reference(node)
        
        
           
        # -- Keywords 
        elif isinstance(node, (PointNode, CircleNode, LineNode, AngleNode)):
            evaluated_args = []
            for arg in node.args:
                evaluated_args.append(self.evaluate(arg))
            return type(node).func(*evaluated_args)
        
        elif isinstance(node, BinaryOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            op = node.op
            return self.BINARY_OPS[op](left, right)
                
        
        # -- Collections
        elif isinstance(node, CollectionNode):
            return node
    
        # -- Constraints
        elif isinstance(node, ConstraintNode):
            # print(node.left)
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            self.solution_set.add_constraint(left, node.operator, right)
            
        elif isinstance(node, QueryNode):
            evaluated_args = []
            for arg in node.args:
                evaluated_args.append(self.evaluate(arg))
            self.solution_set.refine()
            return BUILTINFUNCS[node.func](*evaluated_args)
        
        
        else:
            raise ValueError(f"Unknown AST Node type: {type(node)}. Node: {node}")
            