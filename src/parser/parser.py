from lexer.lexer import TOK_INT, TOK_PLUS, TOK_MINUS, TOK_MUL, TOK_DIV, TOK_LPAREN, TOK_RPAREN, TOK_EOF
from parser.nodes import NumberNode, BinOpNode

# --- PARSER ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_idx = -1
        self.advance()

    def advance(self):
        self.token_idx += 1
        if self.token_idx < len(self.tokens):
            self.current_token = self.tokens[self.token_idx]
        return self.current_token

    def factor(self):
        token = self.current_token

        if token.type == TOK_INT:
            self.advance()
            return NumberNode(token)

        if token.type == TOK_LPAREN:
            self.advance()
            expr = self.expr()
            if self.current_token.type == TOK_RPAREN:
                self.advance()
                return expr
            else:
                raise Exception("Expected ')'")
        
        raise Exception(f"Expected int or '(', found {token}")

    def term(self):
        return self.bin_op(self.factor, (TOK_MUL, TOK_DIV))

    def expr(self):
        return self.bin_op(self.term, (TOK_PLUS, TOK_MINUS))

    def bin_op(self, func, ops):
        left = func()

        while self.current_token.type in ops:
            op_token = self.current_token
            self.advance()
            right = func()
            left = BinOpNode(left, op_token, right)

        return left

    def parse(self):
        return self.expr()
