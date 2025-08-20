# main.py
import sys
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.solver import Solver
from src.builtinFuncs import printout

def main():

    if len(sys.argv) < 2:
        print("Usage: python main.py filename.ekl")
        sys.exit(1)
        
    filename = sys.argv[1]

    # filename = 'test2.ekl'
    
    try:
        with open(filename, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        printout(f'File not found: {filename}')
        sys.exit(1)
        
    # --- Lexing ---
    lexer = Lexer(code)
    tokens = lexer.generate_tokens()
    # print(tokens)
    
    # --- Parsing ---
    parser = Parser(tokens)
    try:
        ast_nodes = parser.parseTokens()
    except Exception as e:
        # printout(f'Parser error: {e
        raise e
    # print("NODES:")
    # print(ast_nodes)
    
    # --- Interpreting ---
    interpreter = Interpreter()
    interpreter.run(ast_nodes)
    
    # --- Solving ---
    # print("SYMBOLS:")
    # print(solver.symbols)
    # print("CONSTRAINTS:")
    # print(solver.constraints)
    # solutions = solver.solve()
    # print(solutions)
    

if __name__ == "__main__":
    main()   