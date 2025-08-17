from enum import Enum, auto

class TokenType(Enum):
    """Enum representing different types of tokens."""
    IDENTIFIER = auto()
    KEYWORD = auto()
    NUMBER = auto()
    LPAREN = auto()  # Left Parenthesis
    RPAREN = auto()  # Right Parenthesis
    PLUS = auto()     # Plus Operator
    MINUS = auto()    # Minus Operator
    INTERSECT = auto() # Multiplication Operator
    SLASH = auto()   # Division Operator
    EQUALS = auto()   # Assignment Operator
    COMMA = auto()    # Comma
    UNKNOWN = auto()
    CARAT = auto()
    AT = auto()
    
    EOF = auto()