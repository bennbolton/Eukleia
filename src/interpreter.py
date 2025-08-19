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
        # Numbers
        if isinstance(node, NumberNode):
            return node
        
        
        
        elif isinstance(node, ObjectDefinition):
            obj = node.obj if (not isinstance(node.obj, ASTNode)) or isinstance(node.obj, (CollectionNode, )) else self.evaluate(node.obj)
            value = node.value if not isinstance(node.obj, ASTNode) or isinstance(node.obj, (CollectionNode, )) else self.evaluate(node.value)
            # Handle Collections
            if isinstance(obj, CollectionNode):
                # Both Collections
                if isinstance(value, CollectionNode):
                    if len(obj) == len(value):
                        for i in range(len(obj)):
                            self.evaluate(ObjectDefinition(obj.items[i], value.items[i]))
                    else:
                        raise ValueError(f"Mismatched Collection Sizes: {len(obj)} and {len(value)}")
                # Collection = value
                else:
                    for i in range(len(obj)):
                        self.evaluate(ObjectDefinition(obj.items[i], value))
            # Obj = Collection
            elif isinstance(value, CollectionNode):
                self.symbols[obj] = Collection(value.items)
            # Stanadrd A = B
            else:
                self.symbols[obj] = value
        
        elif isinstance(node, ObjectReference):
            value = self.symbols.get(node.name)
            if value is None:
                return node.name
            return self.evaluate(value)
        
        
        elif isinstance(node, PointNode):
            return make_point(*node.args)
        
        elif isinstance(node, CollectionNode):
            pass
        
        
            
        
        
        
        
        # elif isinstance(node, ObjectDefinition):
        #     value = self.evaluate(node.value) if isinstance(node.value, ASTNode) else node.value
        #     self.symbols[node.name] = value
        #     # print(f"Defined object {node.name} = {node.value}")
        
        # elif isinstance(node, VariableDefinition):
        #     if isinstance(node.value, NumberNode):
        #         self.symbols[node.name] = node.value
        #         # print(f"Defined variable {node.name} = {node.value}")
        #     else:
        #         value = self.evaluate(node.value)
        #         if isinstance(value, Object):
        #             raise NameError(f"Variables cannot be Objects")
        #         self.symbols[node.name] = value
            
        
        # elif isinstance(node, (ObjectReference, VariableReference)):
        #     value = self.symbols.get(node.name)
        #     if value is None:
        #         raise NameError(f"name: '{node.name}' is not defined")
        #     return self.evaluate(value)
        
        # elif isinstance(node, QueryNode):
            
        #     args = [self.evaluate(arg) if isinstance(arg, ASTNode) else arg for arg in node.args]

        #     # print(f"Query: {node.function}({', '.join(map(str, args))})")
        #     func = BUILTINS.get(node.function)
        #     if func:
        #         return func(*args)
        #     else:
        #         raise NameError(f"Unknown function '{node.function}'")

        elif isinstance(node, ConstraintNode):
            self.constraints.append(node)
        else:
            raise ValueError(f"Unknown AST Node type: {type(node)}. Node: {node}")
            