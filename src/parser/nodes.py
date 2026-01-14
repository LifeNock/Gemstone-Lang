# --- NODES ---
class NumberNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self): return f'{self.token}'

class StringNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self): return f'{self.token}'

class BinOpNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
    def __repr__(self): return f'({self.left_node}, {self.op_token}, {self.right_node})'

class VarAccessNode:
    def __init__(self, var_name_token):
        self.var_name_token = var_name_token
    def __repr__(self): return f'{self.var_name_token}'

class VarAssignNode:
    def __init__(self, var_name_token, value_node):
        self.var_name_token = var_name_token
        self.value_node = value_node
    def __repr__(self): return f'(mem {self.var_name_token} = {self.value_node})'

class EmitNode:
    def __init__(self, node_to_print):
        self.node_to_print = node_to_print
    def __repr__(self): return f'(emit {self.node_to_print})'

class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case
    def __repr__(self): return f'(if {self.cases} else {self.else_case})'

class WhileNode:
    def __init__(self, condition_node, body_nodes):
        self.condition_node = condition_node
        self.body_nodes = body_nodes
    def __repr__(self): return f'(while {self.condition_node} do {self.body_nodes})'

class FuncDefNode:
    def __init__(self, var_name_token, arg_tokens, body_nodes):
        self.var_name_token = var_name_token
        self.arg_tokens = arg_tokens
        self.body_nodes = body_nodes
    def __repr__(self): return f'(def {self.var_name_token}({self.arg_tokens}))'

class FuncCallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes
    def __repr__(self): return f'(call {self.node_to_call} args={self.arg_nodes})'

class ReturnNode:
    def __init__(self, node_to_return):
        self.node_to_return = node_to_return
    def __repr__(self): return f'(return {self.node_to_return})'
