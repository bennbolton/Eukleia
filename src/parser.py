from tokens import TokenType
from AST import *

class Parser:
    OPERATOR_PRECEDENCE = {
        "==": 1,
        "+": 10,
        "-": 10,
        "*": 20,
        "/": 20
    }
    BINARY_OPERATORS = {TokenType.PLUS, TokenType.MINUS, TokenType.SLASH, TokenType.ASTERISK}
    DEF_AND_CON = {TokenType.PARALLEL, TokenType.EQUALS_DOUBLE, TokenType.EQUALS_SINGLE}
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        if self.pos + offset >= len(self.tokens):
            return None
        return self.tokens[self.pos + offset]

    def advance(self):
        token = self.peek()
        if token is not None:
            self.pos += 1
        return token

    def expect(self, tType, value=None):
        if type(tType) not in [list, tuple]:
            tType = [tType]
        token = self.advance()
        if not token or token.type not in tType or (value is not None and token.value != value):
            raise SyntaxError(f'Expected token {tType} with value {value}, got {token}')
        return token

    def parseTokens(self):
        astNodes = []
        while (tok := self.peek()) and tok.type != TokenType.EOF:
            # Skip comments
            if tok.type == TokenType.HASH:
                while (peek_tok := self.peek()) and peek_tok.type not in (TokenType.NEWLINE, TokenType.EOF):
                    self.advance()
                self.advance()  # consume newline or EOF after comment
                continue
            # Skip newlines
            if tok.type == TokenType.NEWLINE:
                self.advance()
                continue
            # Parse statements
            node = self.parseStatement()
            if node is not None:
                astNodes.append(node)
        return astNodes

    def parseStatement(self):
        # VariableDefinition, ObjectDefinition, Constraint, QueryStatement, ShorthandDefinition, etc.
        left_expr = self.parseExpression()
        tok = self.peek()
        
        if tok and tok.type in self.DEF_AND_CON:
            op_tok = self.advance()
            rhs_expr = self.parseExpression()
            if op_tok.type == TokenType.EQUALS_SINGLE:
                if isinstance(left_expr, VariableReference):
                    return VariableDefinition(left_expr, rhs_expr)
                else:
                    return ObjectDefinition(left_expr, rhs_expr)
            else:
                return ConstraintNode(left_expr, op_tok.value, rhs_expr)
        # Non declarative statements
        else:
            raise SyntaxError("Not sure what you're going for")
            

    def parseExpression(self, precedence=0):
        # Placeholder for expression parsing logic
        # This method should handle parsing of expressions including:
        # BinaryOp, FunctionCall, AngleNode, LineNode, CircleNode, etc.
        # For now, simply parse a primary expression
        left = self.parsePrimary()
        
        
        
        # Check for a comma immediately after a primary expression
        if (next_tok := self.peek()) and next_tok.type == TokenType.COMMA:
            exprs = [left]
            while (next_tok := self.peek()) and next_tok.type == TokenType.COMMA:
                self.advance()  # consume comma
                exprs.append(self.parseExpression())  # parse each element as a primary
            left = CollectionNode(exprs)  # wrap into a collection node
        
        
        
        while True:
            op_tok = self.peek()
            if not op_tok or op_tok.type not in self.BINARY_OPERATORS:
                break
            op_precedence = self.OPERATOR_PRECEDENCE[op_tok.value]
            if op_precedence < precedence:
                break
            self.advance()
            right = self.parseExpression(op_precedence + 1)
            left = BinaryOp(left, op_tok.value, right)

        return left

    def parsePrimary(self):
        # Placeholder for primary expression parsing
        # This method should parse:
        # Number, Unknown, VariableReference, ObjectReference, PointNode, etc.
        tok = self.peek()
        if tok is None:
            raise SyntaxError("Unexpected end of input")

        if tok.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(tok.value)
        elif tok.type == TokenType.UNKNOWN:
            self.advance()
            return UnknownNode()
        elif tok.type == TokenType.IDENTIFIER:
            self.advance()
            # Could be VariableReference or FunctionCall
            # Placeholder logic:
            if (next_tok := self.peek()) and next_tok.type == TokenType.LPAREN:
                # Parse function call
                self.advance()  # consume LPAREN
                args = []
                while (arg_tok := self.peek()) and arg_tok.type != TokenType.RPAREN:
                    if arg_tok.type == TokenType.COMMA:
                        self.advance()
                        continue
                    args.append(self.parseExpression())
                self.expect(TokenType.RPAREN)
                return QueryNode(tok.value, args)
            else:
                return VariableReference(tok.value)
        elif tok.type == TokenType.OBJECT:
            self.expect(TokenType.OBJECT)
            # Could be ObjectReference or more complex structure like LineNode
            # AB line shorthand
            if (next_tok := self.peek()) and next_tok.type == TokenType.OBJECT:
                second_tok = self.advance()
                return LineNode(ObjectReference(tok.value), ObjectReference(second_tok.value))
            else:
                return ObjectReference(tok.value)
        elif tok.type == TokenType.LPAREN:
            self.expect(TokenType.LPAREN)
            
            
            
            
            expr = self.parseExpression()
            self.expect(TokenType.RPAREN)
            print(expr)
            if isinstance(expr, CollectionNode) and len(expr) == 2:
                return PointNode(expr.items[0], expr.items[1])
            else:
                return expr
            
       
        elif tok.type == TokenType.KEYWORD:
            self.advance()
            # Parse keyword-based nodes like CircleNode, AngleNode, QueryStatement
            self.expect(TokenType.LPAREN)
            args = self.parseExpression()
            if isinstance(args, CollectionNode):
                args = args.items
            self.expect(TokenType.RPAREN)
            # Example for CircleNode
            if tok.value == "Circle":
                return CircleNode(*args)
            elif tok.value == "Angle":
                return AngleNode(*args)
            else:
                return QueryNode(tok.value, args)
        elif tok.type == TokenType.ANGLE:
            self.expect(TokenType.ANGLE)
            p1_tok = ObjectReference(self.expect(TokenType.OBJECT).value)
            vertex_tok = ObjectReference(self.expect(TokenType.OBJECT).value)
            p2_tok = ObjectReference(self.expect(TokenType.OBJECT).value)
            return AngleNode(p1_tok, vertex_tok, p2_tok)
        else:
            raise SyntaxError(f"Unexpected token {tok} in primary expression")