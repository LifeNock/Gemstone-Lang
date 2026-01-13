import sys
from lexer.lexer import Lexer, TOK_EOF

# --- REPL ---
def main():
    while True:
        try:
            text = input('Gemstone > ')
        except EOFError:
            break

        if not text or text.lower() == 'exit':
            break

        lexer = Lexer(text)

        try:
            token = lexer.get_next_token()
            while token.type != TOK_EOF:
                print(token)
                token = lexer.get_next_token()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    main()
