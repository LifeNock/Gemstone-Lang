import sys
from lexer.lexer import Lexer, TOK_EOF
from parser.parser import Parser
from interpreter.interpreter import Interpreter
from interpreter.stdlib import load_stdlib

def run(text, interpreter, is_file=False):
    lexer = Lexer(text)
    tokens = []
    try:
        token = lexer.get_next_token()
        while token.type != TOK_EOF:
            tokens.append(token)
            token = lexer.get_next_token()
        tokens.append(token)
    except Exception as e:
        print(f"Lexer Error: {e}")
        return

    if not tokens: return

    parser = Parser(tokens)
    try:
        nodes = parser.parse()
    except Exception as e:
        print(f"Parser Error: {e}")
        return

    try:
        for node in nodes:
            result = interpreter.visit(node)
            if not is_file and result is not None:
                print(result)
    except Exception as e:
        print(f"Runtime Error: {e}")

def main():
    interpreter = Interpreter()
    load_stdlib(interpreter.global_symbol_table)
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                script = f.read()
            run(script, interpreter, is_file=True)
        except FileNotFoundError:
            print(f"Could not find file: {filename}")
    else:
        print("Gemstone Compiler v0.5")
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
