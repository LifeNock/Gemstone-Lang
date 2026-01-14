from lexer.lexer import *
from parser.nodes import *

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
        else:
            self.current_token = Token(TOK_EOF)
        return self.current_token

    def check_token(self, type_):
        return self.current_token.type == type_

    def check_keyword(self, value):
        return self.current_token.matches(TOK_KEYWORD, value)

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
            raise Exception("Expected ')'")
        
        raise Exception(f"Expected int, float, string, identifier or '(', found {token}")

    def call(self):
        atom = self.atom()
        
        if self.current_token.type == TOK_LPAREN:
            self.advance()
            arg_nodes = []
            
            if self.current_token.type == TOK_RPAREN:
                self.advance()
            else:
                arg_nodes.append(self.expr())
                while self.current_token.type == TOK_COMMA:
                    self.advance()
                    arg_nodes.append(self.expr())
                
                if self.current_token.type != TOK_RPAREN:
                    raise Exception("Expected ')'")
                self.advance()
            return FuncCallNode(atom, arg_nodes)
        
        return atom

    def term(self):
        return self.bin_op(self.call, (TOK_MUL, TOK_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TOK_PLUS, TOK_MINUS))

    def comp_expr(self):
        if self.current_token.matches(TOK_KEYWORD, 'if'):
            return self.if_expr()
        if self.current_token.matches(TOK_KEYWORD, 'while'):
            return self.while_expr()
        if self.current_token.matches(TOK_KEYWORD, 'def'):
            return self.func_def()
        if self.current_token.matches(TOK_KEYWORD, 'return'):
            return self.return_expr()
            
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

        return self.comp_expr()

    def block(self):
        statements = []
        while not self.check_keyword('end') and not self.check_keyword('else') and not self.check_token(TOK_EOF):
            statements.append(self.expr())
        return statements

    def if_expr(self):
        self.advance()
        condition = self.comp_expr()

        if not self.check_keyword('then'):
            raise Exception("Expected 'then'")
        self.advance()

        true_block = self.block()
        else_block = None

        if self.check_keyword('else'):
            self.advance()
            else_block = self.block()

        if not self.check_keyword('end'):
             raise Exception("Expected 'end' after if-block")
        self.advance()

        return IfNode([(condition, true_block)], else_block)

    def while_expr(self):
        self.advance()
        condition = self.comp_expr()

        if not self.check_keyword('do'):
            raise Exception("Expected 'do'")
        self.advance()

        body = self.block()

        if not self.check_keyword('end'):
            raise Exception("Expected 'end' after while-block")
        self.advance()

        return WhileNode(condition, body)

    def func_def(self):
        self.advance()

        if self.current_token.type != TOK_IDENTIFIER:
            raise Exception("Expected function name")
        
        var_name_token = self.current_token
        self.advance()

        if self.current_token.type != TOK_LPAREN:
             raise Exception("Expected '('")
        self.advance()

        arg_tokens = []
        if self.current_token.type == TOK_IDENTIFIER:
            arg_tokens.append(self.current_token)
            self.advance()
            while self.current_token.type == TOK_COMMA:
                self.advance()
                if self.current_token.type != TOK_IDENTIFIER:
                    raise Exception("Expected argument name")
                arg_tokens.append(self.current_token)
                self.advance()
        
        if self.current_token.type != TOK_RPAREN:
             raise Exception("Expected ')'")
        self.advance()

        body = self.block()

        if not self.check_keyword('end'):
             raise Exception("Expected 'end' after function body")
        self.advance()

        return FuncDefNode(var_name_token, arg_tokens, body)
    
    def return_expr(self):
        self.advance()
        expr = self.expr()
        return ReturnNode(expr)

    def bin_op(self, func, ops):
        left = func()
        while self.current_token.type in ops:
            op_token = self.current_token
            self.advance()
            right = func()
            left = BinOpNode(left, op_token, right)
        return left

    def parse(self):
        statements = []
        while self.current_token.type != TOK_EOF:
            statements.append(self.expr())
        return statements
