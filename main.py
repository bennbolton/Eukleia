# main.py
import sys
from src.eukleia import Eukleia

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
        print(f'File not found: {filename}')
        sys.exit(1)
    

    program = Eukleia()
    program.run(code, False)
    

if __name__ == "__main__":
    main()   