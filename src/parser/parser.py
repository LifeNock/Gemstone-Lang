from lexer.lexer import *
from parser.nodes import NumberNode, StringNode, BinOpNode, VarAssignNode, VarAccessNode, EmitNode, IfNode

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

    def atom(self):
        token = self.current_token

        if token.type in (TOK_INT, TOK_FLOAT):
            self.advance()
            return NumberNode(token)
        
        if token.type == TOK_STRING:
            self.advance()
            return StringNode(token)

        if token.type == TOK_IDENTIFIER:
            self.advance()
            return VarAccessNode(token)

        if token.type == TOK_LPAREN:
            self.advance()
            expr = self.expr()
            if self.current_token.type == TOK_RPAREN:
                self.advance()
                return expr
            else:
                raise Exception("Expected ')'")
        
        raise Exception(f"Expected int, float, string, identifier or '(', found {token}")

    def term(self):
        return self.bin_op(self.atom, (TOK_MUL, TOK_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TOK_PLUS, TOK_MINUS))

    def comp_expr(self):
        if self.current_token.matches(TOK_KEYWORD, 'if'):
            return self.expr()
            
        node = self.bin_op(self.arith_expr, (TOK_EE, TOK_NE, TOK_LT, TOK_GT, TOK_LTE, TOK_GTE))
        return node

    def expr(self):
        if self.current_token.matches(TOK_KEYWORD, 'mem'):
            self.advance()
            if self.current_token.type != TOK_IDENTIFIER:
                raise Exception("Expected identifier after 'mem'")
            
            var_name = self.current_token
            self.advance()

            if self.current_token.type != TOK_EQ:
                raise Exception("Expected '='")
            
            self.advance()
            expr = self.expr()
            return VarAssignNode(var_name, expr)

        elif self.current_token.matches(TOK_KEYWORD, 'emit'):
            self.advance()
            expr = self.expr()
            return EmitNode(expr)

        elif self.current_token.matches(TOK_KEYWORD, 'if'):
            self.advance()
            condition = self.comp_expr()

            if not self.current_token.matches(TOK_KEYWORD, 'then'):
                raise Exception(f"Expected 'then', found {self.current_token}")

            self.advance()
            expr = self.expr()
            return IfNode([(condition, expr)], None)

        return self.comp_expr()

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
