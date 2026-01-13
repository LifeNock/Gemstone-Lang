from lexer.lexer import TOK_PLUS, TOK_MINUS, TOK_MUL, TOK_DIV
from parser.nodes import NumberNode, BinOpNode, VarAssignNode, VarAccessNode, EmitNode

# --- INTERPRETER ---
class Interpreter:
    def __init__(self):
        self.symbol_table = {}

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node):
        return node.token.value

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

    def visit_VarAssignNode(self, node):
        var_name = node.var_name_token.value
        value = self.visit(node.value_node)
        self.symbol_table[var_name] = value
        return value

    def visit_VarAccessNode(self, node):
        var_name = node.var_name_token.value
        value = self.symbol_table.get(var_name)
        if value is None:
            raise Exception(f"'{var_name}' is not defined")
        return value

    def visit_EmitNode(self, node):
        value = self.visit(node.node_to_print)
        print(value)
        return value
