import sys
from lexer.lexer import Lexer, TOK_EOF
from parser.parser import Parser
from interpreter.interpreter import Interpreter

# --- REPL ---
def main():
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

        # 3. Interpreter
        interpreter = Interpreter()
        try:
            result = interpreter.visit(ast)
            print(result)
        except Exception as e:
            print(f"Runtime Error: {e}")

if __name__ == '__main__':
    main()
