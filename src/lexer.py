from .tokens import TokenType

class Token:
    def __init__(self, tType, value=None):
        self.type = tType
        self.value = value
        
    def __repr__(self):
        return f'{self.type.name}: {self.value if self.value is not None else ""}'

class Lexer:
    KEYWORDS = {
        'Circle',
        'Line',
        'Print',
        'Angle',
        'Type',
        'Deg',
        'Rad'
    }
    OPERATORS = {
        '?': TokenType.UNKNOWN,
        '@': TokenType.AT,
        '=': TokenType.EQUALS_SINGLE,
        '==': TokenType.EQUALS_DOUBLE,
        '^': TokenType.CARAT,
        '*': TokenType.ASTERISK,
        '<': TokenType.ANGLE,
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '/': TokenType.SLASH,
        '//': TokenType.PARALLEL

    }
    PUNCTUATION = {
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        ',': TokenType.COMMA,
        '#': TokenType.HASH,
        ':': TokenType.COLON           
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
            if ch == '\n':
                tokens.append(Token(TokenType.NEWLINE))
            if ch.isspace():
                continue
            # if token begins with uppercase letter
            elif ch.isupper():
                ident = ch
                # collect rest of token
                while ((nxt := self.peek()) and ((nxt.isalnum() and not nxt.isupper()) or nxt == '_' )):
                    ident += self.next_char()
                if ident in self.KEYWORDS:
                    tokens.append(Token(TokenType.KEYWORD, ident))
                else:
                    tokens.append(Token(TokenType.OBJECT, ident))
            elif ch.islower() or ch == '_':
                ident = ch
                # collect the rest
                while ((nxt := self.peek()) and (nxt.isalnum() or nxt == '_')):
                    ident += self.next_char()
                tokens.append(Token(TokenType.IDENTIFIER, ident))
                    
            # if token is a number
            elif ch.isdigit() or (ch == '.' and self.peek() and self.peek().isdigit()):
                num = ch
                while ((nxt := self.peek()) and (nxt.isdigit() or nxt == '.')):
                    num += self.next_char()
                tokens.append(Token(TokenType.NUMBER, float(num)))
            # operators
            elif ch in self.OPERATORS:
                occ = 1
                while ((nxt := self.peek()) and nxt in self.OPERATORS and self.OPERATORS[ch] == self.OPERATORS[nxt]):
                    occ += 1
                    self.next_char()
                try:
                    tokens.append(Token(self.OPERATORS[ch*occ], ch*occ))
                except:
                    raise SyntaxError("Too Many operators")
            elif ch in self.PUNCTUATION:
                tokens.append(Token(self.PUNCTUATION[ch], 1))
            else:
                raise Exception(f'Unexpected character: {ch}')
        
        tokens.append(Token(TokenType.EOF))
        return tokens