# main.py
import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

def main():

    # if len(sys.argv) < 2:
    #     print("Usage: python run.py filename.ekl")
    #     sys.exit(1)
        
    # filename = sys.argv[1]

    filename = 'test2.ekl'
    
    try:
        with open(filename, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f'File not found: {filename}')
        sys.exit(1)
        
    # --- Lexing ---
    lexer = Lexer(code)
    tokens = lexer.generate_tokens()
    print(tokens)
    
    # --- Parsing ---
    parser = Parser(tokens)
    try:
        ast_nodes = parser.parseTokens()
    except Exception as e:
        print(f'Parser error: {e}')
        sys.exit(1)
        
    print(ast_nodes)
    interpreter = Interpreter()
    interpreter.run(ast_nodes)
    
    print("SYMBOLS:")
    print(interpreter.symbols)

if __name__ == "__main__":
    main()   