from tokens import TokenType
from AST import *

class Parser:
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
        if type(tType) not in [list, dict, tuple]:
            tType = [tType]
        token = self.advance()
        if not token or token.type not in tType or (value and token.value != value):
            raise SyntaxError(f'Expected token {tType}, got {token}')
        return token
    
    def parseStatement(self):
        tok = self.peek()
        nxt = self.peek(1)
        # Assignment: x = 
        if nxt and nxt.type == TokenType.EQUALS and nxt.value == 1:
            return self.parseAssignment()
        
    def parseAssignment(self):
        assignTok = self.expect([TokenType.IDENTIFIER, TokenType.OBJECT])
        self.expect(TokenType.EQUALS, 1)
        value = self.parseExpression()
        if assignTok.type == TokenType.OBJECT:
            return ObjectDefinition(assignTok.value, value)
        elif assignTok.type == TokenType.IDENTIFIER:
            return VariableDefinition(assignTok.value, value)
    
        
    def parseExpression(self):
        tok = self.advance()
        if tok.type == TokenType.UNKNOWN:
            return Unknown()
        if tok.type == TokenType.NUMBER:
            return Number(tok.value)
        elif tok.type == TokenType.LPAREN:
            # non keyword brackets
            # very strict, be better later
            x_tok = self.expect([TokenType.NUMBER, TokenType.UNKNOWN])
            self.expect(TokenType.COMMA)
            y_tok = self.expect([TokenType.NUMBER, TokenType.UNKNOWN])
            self.expect(TokenType.RPAREN)
            return (x_tok.value if x_tok.type == TokenType.NUMBER else Unknown, y_tok.value if y_tok.type == TokenType.NUMBER else Unknown())
        elif tok.type == TokenType.KEYWORD:
            # function call from keyword
            func_name = tok.value
            self.expect(TokenType.LPAREN)
            args = []
            while (peek_tok := self.peek()) and peek_tok.type != TokenType.RPAREN:
                if peek_tok.type == TokenType.COMMA:
                    self.expect(TokenType.COMMA)
                else:
                    args.append(self.parseExpression())
            self.expect(TokenType.RPAREN)
            return Query(None, func_name, args)
        elif tok.type in [TokenType.IDENTIFIER, TokenType.OBJECT]:
            if tok.type == TokenType.OBJECT:
                return ObjectReference(tok.value)
            elif tok.type == TokenType.IDENTIFIER:
                return VariableReference(tok.value)

        else:
            raise SyntaxError(f'Unexpected token in expression: {tok}')
        
    def parseTokens(self):
        astNodes = []
        
        while (tok := self.peek()) and tok.type != TokenType.EOF:
            if tok.type == TokenType.NEWLINE:
                self.advance()
            elif tok.type in [TokenType.IDENTIFIER, TokenType.OBJECT]:
                node = self.parseStatement()
                astNodes.append(node)
            else: 
                node = self.parseStatement()
                astNodes.append(node)
        return astNodes
            
                