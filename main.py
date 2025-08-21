# main.py
import sys
from src.eukleia import Eukleia
from src.builtinFuncs import printout

def main():

    # if len(sys.argv) < 2:
    #     print("Usage: python main.py filename.ekl")
    #     sys.exit(1)
        
    # filename = sys.argv[1]
    filename = "test2.ekl"
    
    try:
        with open(filename, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        printout(f'File not found: {filename}')
        sys.exit(1)
    

    program = Eukleia()
    program.run(code, True)
    

if __name__ == "__main__":
    main()   