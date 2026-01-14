import sys
from lexer.lexer import Lexer, TOK_EOF
from parser.parser import Parser
from interpreter.interpreter import Interpreter

def run_script(text, interpreter):
    # 1. Lexer
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

    # For multi-line file execution, we need to split by line or handle statements
    # Simple approach: Split by newline and run line by line
    lines = text.split('\n')
    for line in lines:
        if not line.strip(): continue
        
        lexer = Lexer(line)
        tokens = []
        try:
            token = lexer.get_next_token()
            while token.type != TOK_EOF:
                tokens.append(token)
                token = lexer.get_next_token()
        except Exception as e:
            continue # skip empty lines or weird lex errors

        if not tokens: continue

        parser = Parser(tokens)
        try:
            ast = parser.parse()
            result = interpreter.visit(ast)
            if result is not None:
                pass # In file mode, we generally don't print unless emit is called
        except Exception as e:
            print(f"Error: {e}")

def run_repl(interpreter):
    print("Gemstone Compiler v0.2")
    print("Type 'exit' to quit.")

    while True:
        try:
            text = input('Gemstone > ')
        except EOFError:
            break

        if not text or text.lower() == 'exit':
            break

        lexer = Lexer(text)
        tokens = []
        try:
            token = lexer.get_next_token()
            while token.type != TOK_EOF:
                tokens.append(token)
                token = lexer.get_next_token()
        except Exception as e:
            print(f"Lexer Error: {e}")
            continue

        parser = Parser(tokens)
        try:
            ast = parser.parse()
        except Exception as e:
            print(f"Parser Error: {e}")
            continue

        try:
            result = interpreter.visit(ast)
            if result is not None:
                print(result)
        except Exception as e:
            print(f"Runtime Error: {e}")

if __name__ == '__main__':
    interpreter = Interpreter()
    
    if len(sys.argv) > 1:
        # Run File Mode
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                script = f.read()
            run_script(script, interpreter)
        except FileNotFoundError:
            print(f"Could not find file: {filename}")
    else:
        # Run REPL Mode
        run_repl(interpreter)
