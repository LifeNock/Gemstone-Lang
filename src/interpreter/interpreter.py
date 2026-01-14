from lexer.lexer import *
from parser.nodes import *
from .stdlib import BuiltinFunction

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

class Function:
    def __init__(self, name, body_nodes, arg_names):
        self.name = name
        self.body_nodes = body_nodes
        self.arg_names = arg_names
    def __repr__(self): return f"<function {self.name}>"

class ReturnValue:
    def __init__(self, value): self.value = value

class Interpreter:
    def __init__(self):
        self.global_symbol_table = SymbolTable()
        self.current_symbol_table = self.global_symbol_table

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self, node):
        return node.token.value

    def visit_StringNode(self, node):
        return node.token.value

    def visit_ListNode(self, node):
        return [self.visit(e) for e in node.element_nodes]

    def visit_DictNode(self, node):
        return {self.visit(k): self.visit(v) for k, v in node.key_value_pairs}

    def visit_BinOpNode(self, node):
        left = self.visit(node.left_node)
        right = self.visit(node.right_node)

        if node.op_token.type == TOK_PLUS: return left + right
        elif node.op_token.type == TOK_MINUS: return left - right
        elif node.op_token.type == TOK_MUL: return left * right
        elif node.op_token.type == TOK_DIV: return left / right
        elif node.op_token.type == TOK_EE: return 1 if left == right else 0
        elif node.op_token.type == TOK_NE: return 1 if left != right else 0
        elif node.op_token.type == TOK_LT: return 1 if left < right else 0
        elif node.op_token.type == TOK_GT: return 1 if left > right else 0
        elif node.op_token.type == TOK_LTE: return 1 if left <= right else 0
        elif node.op_token.type == TOK_GTE: return 1 if left >= right else 0

    def visit_VarAssignNode(self, node):
        var_name = node.var_name_token.value
        value = self.visit(node.value_node)
        self.current_symbol_table.set(var_name, value)
        return value

    def visit_VarAccessNode(self, node):
        var_name = node.var_name_token.value
        value = self.current_symbol_table.get(var_name)
        if value is None: raise Exception(f"'{var_name}' is not defined")
        return value

    def visit_IndexAccessNode(self, node):
        left = self.visit(node.left_node)
        index = self.visit(node.index_node)
        try: return left[index]
        except: raise Exception(f"Cannot access index {index} of {left}")

    def visit_MemberAccessNode(self, node):
        left = self.visit(node.left_node)
        member = node.member_name_token.value
        if isinstance(left, dict) and member in left:
            return left[member]
        raise Exception(f"Cannot access property '{member}' of {left}")

    def visit_EmitNode(self, node):
        value = self.visit(node.node_to_print)
        print(value)
        return None

    def visit_IfNode(self, node):
        for condition, statement_list in node.cases:
            if self.visit(condition):
                for stmt in statement_list:
                    res = self.visit(stmt)
                    if isinstance(res, ReturnValue): return res
                return None
        if node.else_case:
            for stmt in node.else_case:
                res = self.visit(stmt)
                if isinstance(res, ReturnValue): return res
        return None

    def visit_WhileNode(self, node):
        while True:
            condition = self.visit(node.condition_node)
            if not condition: break
            for stmt in node.body_nodes:
                res = self.visit(stmt)
                if isinstance(res, ReturnValue): return res
        return None

    def visit_ForNode(self, node):
        iterator = self.visit(node.iterator_node)
        var_name = node.var_name_token.value
        
        if not isinstance(iterator, list) and not isinstance(iterator, str):
            raise Exception(f"Cannot iterate over {iterator}")
            
        for item in iterator:
            self.current_symbol_table.set(var_name, item)
            for stmt in node.body_nodes:
                res = self.visit(stmt)
                if isinstance(res, ReturnValue): return res
        return None

    def visit_FuncDefNode(self, node):
        func_name = node.var_name_token.value
        arg_names = [arg.value for arg in node.arg_tokens]
        func = Function(func_name, node.body_nodes, arg_names)
        self.current_symbol_table.set(func_name, func)
        return func

    def visit_FuncCallNode(self, node):
        function = self.visit(node.node_to_call)
        args = [self.visit(arg) for arg in node.arg_nodes]

        if isinstance(function, BuiltinFunction):
            return function.func(self, args)

        if isinstance(function, Function):
            if len(args) != len(function.arg_names):
                raise Exception(f"Function {function.name} expects {len(function.arg_names)} args")
            return self.call_function(function, args)
        
        raise Exception(f"Not a function: {function}")

    def call_function(self, function, args):
        new_scope = SymbolTable(parent=self.global_symbol_table)
        for i in range(len(args)):
            new_scope.set(function.arg_names[i], args[i])
        previous_scope = self.current_symbol_table
        self.current_symbol_table = new_scope
        result = None
        try:
            for stmt in function.body_nodes:
                res = self.visit(stmt)
                if isinstance(res, ReturnValue):
                    result = res.value
                    break
        finally:
            self.current_symbol_table = previous_scope
        return result
    
    def visit_ReturnNode(self, node):
        value = self.visit(node.node_to_return)
        return ReturnValue(value)
