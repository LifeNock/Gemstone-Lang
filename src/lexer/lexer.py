import string

# --- TOKENS ---
TOK_INT        = 'INT'
TOK_FLOAT      = 'FLOAT'
TOK_STRING     = 'STRING'
TOK_PLUS       = 'PLUS'
TOK_MINUS      = 'MINUS'
TOK_MUL        = 'MUL'
TOK_DIV        = 'DIV'
TOK_LPAREN     = 'LPAREN'
TOK_RPAREN     = 'RPAREN'
TOK_IDENTIFIER = 'IDENTIFIER'
TOK_KEYWORD    = 'KEYWORD'
TOK_EQ         = 'EQ'
TOK_EE         = 'EE'
TOK_NE         = 'NE'
TOK_LT         = 'LT'
TOK_GT         = 'GT'
TOK_LTE        = 'LTE'
TOK_GTE        = 'GTE'
TOK_EOF        = 'EOF'

KEYWORDS = [
    'mem',
    'emit',
    'if',
    'then'
]

# --- CLASSES ---
class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

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

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        self.advance()
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        self.advance()

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TOK_INT, int(num_str))
        else:
            return Token(TOK_FLOAT, float(num_str))

    def make_string(self):
        str_val = ''
        self.advance() 

        while self.current_char is not None and self.current_char != '"':
            str_val += self.current_char
            self.advance()
        
        self.advance()
        return Token(TOK_STRING, str_val)

    def make_identifier(self):
        id_str = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()

        token_type = TOK_KEYWORD if id_str in KEYWORDS else TOK_IDENTIFIER
        return Token(token_type, id_str)

    def make_not_equals(self):
        if self.peek() == '=':
            self.advance()
            self.advance()
            return Token(TOK_NE)
        self.advance()
        return None 

    def make_equals(self):
        token_type = TOK_EQ
        if self.peek() == '=':
            self.advance()
            token_type = TOK_EE
        self.advance()
        return Token(token_type)

    def make_less_than(self):
        token_type = TOK_LT
        if self.peek() == '=':
            self.advance()
            token_type = TOK_LTE
        self.advance()
        return Token(token_type)

    def make_greater_than(self):
        token_type = TOK_GT
        if self.peek() == '=':
            self.advance()
            token_type = TOK_GTE
        self.advance()
        return Token(token_type)

    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '#':
                self.skip_comment()
                continue

            if self.current_char.isdigit():
                return self.make_number()

            if self.current_char == '"':
                return self.make_string()

            if self.current_char.isalpha():
                return self.make_identifier()

            if self.current_char == '!':
                token = self.make_not_equals()
                if token: return token
                raise Exception("Expected '!='")

            if self.current_char == '=':
                return self.make_equals()

            if self.current_char == '<':
                return self.make_less_than()

            if self.current_char == '>':
                return self.make_greater_than()

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
