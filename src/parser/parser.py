from lexer.lexer import *
from parser.nodes import *

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
        
        if token.type == TOK_LBRACKET:
            return self.list_expr()

        if token.type == TOK_LBRACE:
            return self.dict_expr()
        
        raise Exception(f"Unexpected token: {token}")

    def list_expr(self):
        self.advance()
        elements = []
        if self.current_token.type == TOK_RBRACKET:
            self.advance()
        else:
            elements.append(self.expr())
            while self.current_token.type == TOK_COMMA:
                self.advance()
                elements.append(self.expr())
            if self.current_token.type != TOK_RBRACKET:
                raise Exception("Expected ']'")
            self.advance()
        return ListNode(elements)

    def dict_expr(self):
        self.advance()
        pairs = []
        if self.current_token.type == TOK_RBRACE:
            self.advance()
        else:
            key = self.expr()
            if self.current_token.type != TOK_COLON:
                raise Exception("Expected ':' in dict")
            self.advance()
            val = self.expr()
            pairs.append((key, val))
            
            while self.current_token.type == TOK_COMMA:
                self.advance()
                key = self.expr()
                if self.current_token.type != TOK_COLON:
                    raise Exception("Expected ':' in dict")
                self.advance()
                val = self.expr()
                pairs.append((key, val))
                
            if self.current_token.type != TOK_RBRACE:
                raise Exception("Expected '}'")
            self.advance()
        return DictNode(pairs)

    def call(self):
        node = self.atom()
        
        while True:
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
                node = FuncCallNode(node, arg_nodes)
            
            elif self.current_token.type == TOK_LBRACKET:
                self.advance()
                index = self.expr()
                if self.current_token.type != TOK_RBRACKET:
                    raise Exception("Expected ']'")
                self.advance()
                node = IndexAccessNode(node, index)

            elif self.current_token.type == TOK_DOT:
                self.advance()
                if self.current_token.type != TOK_IDENTIFIER:
                    raise Exception("Expected member identifier")
                member = self.current_token
                self.advance()
                node = MemberAccessNode(node, member)
            
            else:
                break
        
        return node

    def factor(self):
        token = self.current_token
        if token.type in (TOK_PLUS, TOK_MINUS):
            self.advance()
            factor = self.factor()
            return UnaryOpNode(token, factor)
        return self.call()

    def term(self):
        return self.bin_op(self.factor, (TOK_MUL, TOK_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TOK_PLUS, TOK_MINUS))

    def comp_expr(self):
        if self.current_token.matches(TOK_KEYWORD, 'if'):
            return self.if_expr()
        if self.current_token.matches(TOK_KEYWORD, 'while'):
            return self.while_expr()
        if self.current_token.matches(TOK_KEYWORD, 'for'):
            return self.for_expr()
        if self.current_token.matches(TOK_KEYWORD, 'def'):
            return self.func_def()
        if self.current_token.matches(TOK_KEYWORD, 'return'):
            return self.return_expr()
            
        node = self.bin_op(self.arith_expr, (TOK_EE, TOK_NE, TOK_LT, TOK_GT, TOK_LTE, TOK_GTE))
        return node

    def expr(self):
        if self.current_token.matches(TOK_KEYWORD, 'mem'):
            self.advance()
            
            # --- UPDATED ASSIGNMENT LOGIC ---
            # 1. Parse the "Target" (variable, array index, or object property)
            target = self.atom()
            
            # Allow modifiers (.x or [i])
            while self.current_token.type in (TOK_DOT, TOK_LBRACKET):
                if self.current_token.type == TOK_LBRACKET:
                    self.advance()
                    index = self.expr()
                    if self.current_token.type != TOK_RBRACKET: raise Exception("Expected ']'")
                    self.advance()
                    target = IndexAccessNode(target, index)
                elif self.current_token.type == TOK_DOT:
                    self.advance()
                    if self.current_token.type != TOK_IDENTIFIER: raise Exception("Expected identifier")
                    member_name = self.current_token
                    self.advance()
                    target = MemberAccessNode(target, member_name)

            if self.current_token.type != TOK_EQ:
                raise Exception("Expected '='")
            
            self.advance()
            value = self.expr()
            return VarAssignNode(target, value)

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
        if not self.check_keyword('then'): raise Exception("Expected 'then'")
        self.advance()
        true_block = self.block()
        else_block = None
        if self.check_keyword('else'):
            self.advance()
            else_block = self.block()
        if not self.check_keyword('end'): raise Exception("Expected 'end'")
        self.advance()
        return IfNode([(condition, true_block)], else_block)

    def while_expr(self):
        self.advance()
        condition = self.comp_expr()
        if not self.check_keyword('do'): raise Exception("Expected 'do'")
        self.advance()
        body = self.block()
        if not self.check_keyword('end'): raise Exception("Expected 'end'")
        self.advance()
        return WhileNode(condition, body)

    def for_expr(self):
        self.advance()
        if self.current_token.type != TOK_IDENTIFIER: raise Exception("Expected iter var")
        var_name = self.current_token
        self.advance()
        if not self.check_keyword('in'): raise Exception("Expected 'in'")
        self.advance()
        iterator = self.expr()
        if not self.check_keyword('do'): raise Exception("Expected 'do'")
        self.advance()
        body = self.block()
        if not self.check_keyword('end'): raise Exception("Expected 'end'")
        self.advance()
        return ForNode(var_name, iterator, body)

    def func_def(self):
        self.advance()
        if self.current_token.type != TOK_IDENTIFIER: raise Exception("Expected function name")
        var_name_token = self.current_token
        self.advance()
        if self.current_token.type != TOK_LPAREN: raise Exception("Expected '('")
        self.advance()
        arg_tokens = []
        if self.current_token.type == TOK_IDENTIFIER:
            arg_tokens.append(self.current_token)
            self.advance()
            while self.current_token.type == TOK_COMMA:
                self.advance()
                if self.current_token.type != TOK_IDENTIFIER: raise Exception("Expected argument name")
                arg_tokens.append(self.current_token)
                self.advance()
        if self.current_token.type != TOK_RPAREN: raise Exception("Expected ')'")
        self.advance()
        body = self.block()
        if not self.check_keyword('end'): raise Exception("Expected 'end'")
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
