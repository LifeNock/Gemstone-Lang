import sys
from lexer.lexer import Lexer, TOK_EOF
from parser.parser import Parser
from interpreter.interpreter import Interpreter

# --- REPL ---
def main():
    # MOVE THIS LINE UP (Outside the loop)
    # This ensures the memory persists between commands
    interpreter = Interpreter()

    print("Gemstone Compiler v0.1")
    print("Type 'exit' to quit.")

    while True:
        try:
            text = input('Gemstone > ')
        except EOFError:
            break

        if not text or text.lower() == 'exit':
            break

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
            continue

        # 2. Parser
        parser = Parser(tokens)
        try:
            ast = parser.parse()
        except Exception as e:
            print(f"Parser Error: {e}")
            continue

        # 3. Interpreter (Now we just use the existing one)
        try:
            result = interpreter.visit(ast)
            if result is not None:
                print(result)
        except Exception as e:
            print(f"Runtime Error: {e}")

if __name__ == '__main__':
    main()
