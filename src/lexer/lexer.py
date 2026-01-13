import sys

# --- TOKENS ---
TOK_INT       = 'INT'
TOK_PLUS      = 'PLUS'
TOK_MINUS     = 'MINUS'
TOK_MUL       = 'MUL'
TOK_DIV       = 'DIV'
TOK_LPAREN    = 'LPAREN'
TOK_RPAREN    = 'RPAREN'
TOK_EOF       = 'EOF'

# --- CLASSES ---
class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(TOK_INT, self.integer())

            if self.current_char == '+':
                self.advance()
                return Token(TOK_PLUS)

            if self.current_char == '-':
                self.advance()
                return Token(TOK_MINUS)

            if self.current_char == '*':
                self.advance()
                return Token(TOK_MUL)

            if self.current_char == '/':
                self.advance()
                return Token(TOK_DIV)

            if self.current_char == '(':
                self.advance()
                return Token(TOK_LPAREN)

            if self.current_char == ')':
                self.advance()
                return Token(TOK_RPAREN)

            raise Exception(f'Illegal character: {self.current_char}')

        return Token(TOK_EOF)
