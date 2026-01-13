# --- NODES ---
class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'

class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_token}, {self.right_node})'

class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token

    def __repr__(self):
        return f'{self.var_name_token}'

class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node

    def __repr__(self):
        return f'(mem {self.var_name_token} = {self.value_node})'

class EmitNode:
    def __init__(self, node_to_print):
        self.node_to_print = node_to_print

    def __repr__(self):
        return f'(emit {self.node_to_print})'
