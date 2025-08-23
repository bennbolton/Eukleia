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
    COLOURS = {
        'blue': '\033[34m',
        'red': '\033[31m',
        'yellow': '\033[31m',
        'green': '\033[32m',
        'end': '\033[0m'
    }
    def __init__(self, context):
        self.context = context
        self.solver = self.context.solver

    def printout(self):
        print(self.COLOURS['red'], end="")
        for obj, value in self.print_registry.items():
            label = repr(obj).rjust(10)
            print(f"{self.COLOURS['red']}{label}{self.COLOURS['green']} >>  {self.COLOURS['end']}", end=self.COLOURS['blue'])
            if len(value) == 1:
                print(value[0], '\n')
            elif len(value) == 0:
                print("Undeterminable", "\n")
            else:
                for i, answer in enumerate(value):
                    print(f"{" "*15 if i > 0 else ""}{answer}")
                print()
        print(self.COLOURS['end'], end="")
        
    
    def run(self, nodes):
        for node in nodes:
            self.print_registry = {}
            self.evaluate_node_per_branch(node)
            if self.print_registry:
                solutions = self.solver.solve(list(self.print_registry.keys()))
                for t in solutions:
                    self.print_registry[t] = solutions[t]
                self.printout()
            

            

    def evaluate_node_per_branch(self, node):
        branches = list(self.context.solver.branches)
        for branch in branches:
            self.evaluate(node, branch)
    
    def evaluate(self, node, branch):
        
        # -- Numbers
        if isinstance(node, NumberNode):
            return Number(node.value)
        
        elif isinstance(node, (ObjectReference, VariableReference)):
                val = branch.symbols.get(node.name)
                if val is None:
                    self.evaluate(ObjectDefinition(node, Point(node.name)), branch)
                    return branch.symbols.get(node.name)
                else:
                    return val
        
        if isinstance(node, NotNode):
            if isinstance(node.inner, ConstraintNode):
                left = self.evaluate(node.inner.left, branch)
                op = node.inner.operator
                right = self.evaluate(node.inner.right, branch)
                new_branches = branch.add_constraint(left, f"NOT_{op}", right)
                self.solver.branches.remove(branch)
                self.solver.add_branches(new_branches)
                self.solver.prune()
            else:
                raise ValueError("Not must be paired with a constraint")
                
        
        # -- Object/Variable Definitions
        elif isinstance(node, (ObjectDefinition, VariableDefinition)):
            ident = node.ident if not isinstance(node.ident, ASTNode) or isinstance(node.ident, (CollectionNode, ObjectReference, VariableReference)) else self.evaluate(node.ident, branch)
            value = node.value if not isinstance(node.value, ASTNode) or isinstance(node.value, (CollectionNode, )) else self.evaluate(node.value, branch)
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
                        fresh_value = self.evaluate(node.value, branch)
                        self.evaluate(ObjectDefinition(ident.items[i+1], fresh_value), branch)
                            # Obj = Collection
            elif isinstance(value, CollectionNode):
                branch.add_symbol(ident, Collection(value.items))
            # Stanadrd A = B
            else:
                branch.add_symbol(value)

        elif isinstance(node, PrintNode):
            for arg in node.args:
                evaluated_arg = self.evaluate(arg, branch)
                self.print_registry[evaluated_arg] = []
            
        # -- Keywords 
        elif isinstance(node, PointNode):
            point = Point(node.name)
            return point
        
        elif isinstance(node, LineNode):
            points = [self.evaluate(arg, branch) for arg in node.args]
            line = Line(points)
            return line
        
        elif isinstance(node, AngleNode):
            points = [self.evaluate(arg, branch) for arg in node.args]
            angle = Angle(points)
            return angle
        
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
            branch.add_constraint(Constraint(left, node.operator, right))
            
        elif isinstance(node, QueryNode):
            evaluated_args = []
            for arg in node.args:
                evaluated_args.append(self.evaluate(arg, branch))
            # self.solver.refine()
            return BUILTINFUNCS[node.func](*evaluated_args, context=self.context)
        
        
        else:
            raise ValueError(f"Unknown AST Node type: {type(node)}. Node: {node}")
            