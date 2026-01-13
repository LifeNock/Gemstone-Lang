from lexer.lexer import TOK_INT, TOK_PLUS, TOK_MINUS, TOK_MUL, TOK_DIV
from parser.nodes import NumberNode, BinOpNode

# --- INTERPRETER ---
class Interpreter:
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node):
        return int(node.token.value)

    def visit_BinOpNode(self, node):
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)

        if node.op_token.type == TOK_PLUS:
            return left + right
        elif node.op_token.type == TOK_MINUS:
            return left - right
        elif node.op_token.type == TOK_MUL:
            return left * right
        elif node.op_token.type == TOK_DIV:
            return left / right
