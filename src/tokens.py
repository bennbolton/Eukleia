from enum import Enum, auto

class TokenType(Enum):
    """Enum representing different types of tokens."""
    IDENTIFIER = auto()
    OBJECT = auto()
    KEYWORD = auto()
    NUMBER = auto()
    LPAREN = auto()  # Left Parenthesis
    RPAREN = auto()  # Right Parenthesis
    PLUS = auto()     # Plus Operator
    MINUS = auto()    # Minus Operator
    ASTERISK = auto() # Multiplication Operator
    SLASH = auto()   # Division Operator
    PARALLEL = auto()
    EQUALS_SINGLE = auto()   # Assignment Operator
    EQUALS_DOUBLE = auto()
    COMMA = auto()    # Comma
    ANGLE = auto()
    UNKNOWN = auto()
    CARAT = auto()
    AT = auto()
    NEWLINE = auto()
    HASH = auto()
    COLON = auto()
    
    EOF = auto()