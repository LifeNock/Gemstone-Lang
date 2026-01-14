import sys
from lexer.lexer import Lexer, TOK_EOF
from parser.parser import Parser
from interpreter.interpreter import Interpreter

def run(text, interpreter, is_file=False):
    if is_file:
        print(f"--- DEBUG: Raw Text Length: {len(text)} characters ---")

    # 1. Lexer
    print("--- DEBUG: Starting Lexer ---")
    lexer = Lexer(text)
    tokens = []
    try:
        token = lexer.get_next_token()
        while token.type != TOK_EOF:
            tokens.append(token)
            token = lexer.get_next_token()
    except Exception as e:
        print(f"Lexer Error: {e}")
        return

    print(f"--- DEBUG: Lexer found {len(tokens)} tokens ---")
    if not tokens: 
        print("--- DEBUG: No tokens found. Is the file empty? ---")
        return

    # 2. Parser
    print("--- DEBUG: Starting Parser ---")
    parser = Parser(tokens)
    try:
        nodes = parser.parse()
    except Exception as e:
        print(f"Parser Error: {e}")
        return

    # Check if nodes is actually a list (Fix for version mismatch)
    if not isinstance(nodes, list):
        print("--- DEBUG ERROR: Parser did not return a list! ---")
        print("Please ensure src/parser/parser.py is fully updated.")
        # Fallback for old parser version
        nodes = [nodes] 

    print(f"--- DEBUG: Parser found {len(nodes)} statements ---")

    # 3. Interpreter
    print("--- DEBUG: Starting Interpreter ---")
    try:
        for node in nodes:
            result = interpreter.visit(node)
            if not is_file and result is not None:
                print(result)
    except Exception as e:
        print(f"Runtime Error: {e}")
    
    print("--- DEBUG: Finished ---")

def main():
    interpreter = Interpreter()
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        print(f"--- DEBUG: Attempting to run file: {filename} ---")
        try:
            with open(filename, 'r') as f:
                script = f.read()
            run(script, interpreter, is_file=True)
        except FileNotFoundError:
            print(f"ERROR: Could not find file: {filename}")
    else:
        print("Gemstone Compiler v0.3 (Debug Mode)")
        while True:
            try:
                text = input('Gemstone > ')
            except EOFError:
                break
            if not text or text.lower() == 'exit':
                break
            run(text, interpreter, is_file=False)

if __name__ == '__main__':
    main()
