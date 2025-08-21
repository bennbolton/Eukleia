from .astNodes import *
from .builtinFuncs import *
# from .solver import Solver, SolverBranch
    
class Interpreter:
    
    BINARY_OPS = {
        '+': lambda a,b: Number(a + b),
        '-': lambda a,b: Number(a - b),
        '*': lambda a,b: Number(a * b),
        '/': lambda a,b: Number(a / b),
    }
    def __init__(self, context):
        self.context = context
        self.solver = self.context.solver
        
    
    def run(self, nodes):
        for node in nodes:
            self.solver.refine()
            self.evaluate_node_per_branch(node)

            

    def evaluate_node_per_branch(self, node):
        for branch in self.context.solver.branches:
            self.evaluate(node, branch)
            
    
    def evaluate(self, node, branch):
        
        # -- Numbers
        if isinstance(node, NumberNode):
            return type(node).func(node.value)
        
        elif isinstance(node, (ObjectReference, VariableReference)):
                val = branch.symbols.get(node.name)
                if val is None:
                    self.evaluate(ObjectDefinition(node.name, PointNode(NumberNode(None), NumberNode(None))), branch)
                    return branch.symbols.get(node.name)
                else:
                    return val
        
        if isinstance(node, NotNode):
            if isinstance(node.inner, ConstraintNode):
                left = self.evaluate(node.inner.left, branch)
                op = node.inner.operator
                right = self.evaluate(node.inner.right, branch)
                branch.add_constraint(left, f"NOT_{op}", right)
            else:
                raise ValueError("Not must be paired with a constraint")
                
        
        # -- Object/Variable Definitions
        elif isinstance(node, (ObjectDefinition, VariableDefinition)):
            ident = node.ident if not isinstance(node.ident, ASTNode) or isinstance(node.ident, (CollectionNode, ObjectReference, VariableReference)) else self.evaluate(node.ident, branch)
            value = node.value if not isinstance(node.ident, ASTNode) or isinstance(node.ident, (CollectionNode, )) else self.evaluate(node.value, branch)
            if isinstance(ident, (ObjectReference, VariableReference)): 
                ident = ident.name
            # Handle Collections
            if isinstance(ident, CollectionNode):
                # Both Collections
                if isinstance(value, CollectionNode):
                    if len(ident) == len(value):
                        for i in range(len(ident)):
                            self.evaluate(ObjectDefinition(ident.items[i], value.items[i]), branch)
                    else:
                        raise ValueError(f"Mismatched Collection Sizes: {len(ident)} and {len(value)}")
                # Collection = value
                else:
                    self.evaluate(ObjectDefinition(ident.items[0], value), branch)
                    for i in range(len(ident)-1):
                        fresh_value = self.evaluate(node.value)
                        self.evaluate(ObjectDefinition(ident.items[i+1], fresh_value), branch)
            # Obj = Collection
            elif isinstance(value, CollectionNode):
                branch.add_object(ident, Collection(value.items))
            # Stanadrd A = B
            else:
                branch.add_object(ident, value)

        elif isinstance(node, PrintNode):
            self.solver.refine()
            evaluated_args = []
            for arg in node.args:
                evaluated_arg = self.evaluate(arg, branch)
                evaluated_args.append(evaluated_arg)
            
            type(node).func(*evaluated_args)
        # -- Keywords 
        elif isinstance(node, (PointNode, CircleNode, LineNode, AngleNode)):
            evaluated_args = []
            for arg in node.args:
                evaluated_arg = self.evaluate(arg, branch)
                evaluated_args.append(evaluated_arg)
            return type(node).func(*evaluated_args)
        
        elif isinstance(node, BinaryOp):
            left = self.evaluate(node.left, branch)
            right = self.evaluate(node.right, branch)
            op = node.op
            return self.BINARY_OPS[op](left, right)
                
        
        # -- Collections
        elif isinstance(node, CollectionNode):
            return node
    
        # -- Constraints
        elif isinstance(node, ConstraintNode):
            left = self.evaluate(node.left, branch)
            right = self.evaluate(node.right, branch)
            # self.solver.add_constraint(left, node.operator, right)
            branch.add_constraint(left, node.operator, right)
            
        elif isinstance(node, QueryNode):
            evaluated_args = []
            for arg in node.args:
                evaluated_args.append(self.evaluate(arg, branch))
            # self.solver.refine()
            return BUILTINFUNCS[node.func](*evaluated_args, context=self.context)
        
        
        else:
            raise ValueError(f"Unknown AST Node type: {type(node)}. Node: {node}")
            