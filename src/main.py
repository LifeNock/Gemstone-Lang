import sys
from lexer.lexer import Lexer
from parser.parser import Parser

# --- REPL ---
def main():
    while True:
        try:
            text = input('Gemstone > ')
        except EOFError:
            break

        if not text or text.lower() == 'exit':
            break

        # 1. Generate Tokens
        lexer = Lexer(text)
        tokens = []
        try:
            token = lexer.get_next_token()
            while token.type != 'EOF':
                tokens.append(token)
                token = lexer.get_next_token()
        except Exception as e:
            print(f"Lexer Error: {e}")
            continue

        # 2. Generate AST
        parser = Parser(tokens)
        try:
            ast = parser.parse()
            print(ast)
        except Exception as e:
            print(f"Parser Error: {e}")

if __name__ == '__main__':
    main()
