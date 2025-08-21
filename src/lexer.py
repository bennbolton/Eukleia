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
        'Rad',
        'Triangle',
    } 

    SYMBOLS = {
        '?': TokenType.QUESTION,
        '@': TokenType.AT,
        '=': TokenType.EQUALS_SINGLE,
        '==': TokenType.EQUALS_DOUBLE,
        '^': TokenType.CARAT,
        '*': TokenType.ASTERISK,
        '<': TokenType.ANGLE,
        '+': TokenType.PLUS,
        '-': TokenType.MINUS,
        '/': TokenType.SLASH,
        '//': TokenType.PARALLEL,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        ',': TokenType.COMMA,
        '#': TokenType.HASH,
        ':': TokenType.COLON,
        '.': TokenType.DOT,
        '...': TokenType.ELLIPSIS,

        'on': TokenType.ON,
        'not': TokenType.NOT,
        'and': TokenType.AND,
        'or': TokenType.OR,
    }
    def __init__(self):
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

    def generate_tokens(self, text):
        self.text = text
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
                if ident in self.SYMBOLS:
                    tokens.append(Token(self.SYMBOLS[ident], ident))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, ident))
                    
            # if token is a number
            elif ch.isdigit() or (ch == '.' and self.peek() and self.peek().isdigit()):
                num = ch
                while ((nxt := self.peek()) and (nxt.isdigit() or nxt == '.')):
                    num += self.next_char()
                tokens.append(Token(TokenType.NUMBER, float(num)))
            # Symbols
            elif ch in self.SYMBOLS:
                occ = 1
                while ((nxt := self.peek()) and nxt in self.SYMBOLS and self.SYMBOLS[ch] == self.SYMBOLS[nxt]):
                    occ += 1
                    self.next_char()
                symType = self.SYMBOLS.get(ch*occ)
                if symType is not None:
                    tokens.append(Token(symType, ch*occ))
                else:
                    symType = self.SYMBOLS.get(ch)
                    tokens.extend([Token(symType, ch)]*occ)
            else:
                raise Exception(f'Unexpected character: {ch}')
        
        tokens.append(Token(TokenType.EOF))
        return tokens