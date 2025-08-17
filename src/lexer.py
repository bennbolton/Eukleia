import re
from tokens import TokenType

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        
    def __repr__(self):
        return f'{self.type.name}: {self.value if self.value is not None else ""}'

class Lexer:
    KEYWORDS = {
        'Circle',
        'Line',
    }
    OPERATORS = {
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        ',': TokenType.COMMA,
        '?': TokenType.UNKNOWN,
        '@': TokenType.AT,
        '=': TokenType.EQUALS,
        '^': TokenType.CARAT,
        '*': TokenType.INTERSECT
    }
    def __init__(self, text):
        self.text = text
        self.pos = 0
        
    def next_char(self):
        if self.pos >= len(self.text):
            return None
        ch = self.text[self.pos]
        self.pos += 1
        return ch
    
    def peek(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def generate_tokens(self):
        tokens = []
        
        while (ch := self.next_char()) is not None:
            # ignore whitespace
            if ch.isspace():
                continue
            # if token begins with letter
            elif ch.isupper():
                ident = ch
                # collect rest of token
                while ((nxt := self.peek()) and (nxt.isalnum() or nxt == '_')):
                    ident += self.next_char()
                if ident in self.KEYWORDS:
                    tokens.append(Token(TokenType.KEYWORD, ident))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, ident))
            # if token is a number
            elif ch.isdigit() or (ch == '.' and self.peek() and self.peek().isdigit()):
                num = ch
                while ((nxt := self.peek()) and (nxt.isdigit() or nxt == '.')):
                    num += self.next_char()
                tokens.append(Token(TokenType.NUMBER, float(num)))
            elif ch in self.OPERATORS:
                tokens.append(Token(self.OPERATORS[ch]))
            else:
                raise Exception(f'Unexpected character: {ch}')
        
        tokens.append(Token(TokenType.EOF))
        return tokens

print(Lexer("C = Circle(0,0,     5)").generate_tokens())