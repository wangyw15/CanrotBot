import ast

from .data import DEFAULT_PROMPTS, POKEMON_TYPES
from .methods import PokyMethods
from .model import Effects, EvalResult


class PokyMachine(ast.NodeVisitor):
    """
    运行Poky语言
    """

    stack: list = []
    effects: Effects = {}

    def visit_Attribute(self, node):
        self.generic_visit(node)

        # 默认提示
        if node.value.id == "default_prompt" and isinstance(node.value, ast.Name):
            if node.attr in DEFAULT_PROMPTS:
                self.stack.append(DEFAULT_PROMPTS[node.attr])
            else:
                raise ValueError(f"Invalid default prompt: {node.attr}")

    def visit_Constant(self, node):
        self.stack.append(node.value)

    def visit_Call(self, node):
        self.generic_visit(node)

        # 获取函数参数并从栈中移除
        args: list = self.stack[-len(node.args) :]
        self.stack = self.stack[: -len(node.args)]

        # 更改属性克制效果
        if node.func.id == "change_effectiveness":
            self.effects["effectiveness"] = args[0]

        # 运行一般函数
        elif node.func.id in PokyMethods.__dict__:
            poky_method = PokyMethods.__dict__[node.func.id]
            if isinstance(poky_method, staticmethod):
                self.stack.append(poky_method(args))

        # 不支持的函数
        else:
            raise ValueError(f"Invalid function: {node.func.id}")

    def visit_List(self, node):
        list_len = 0
        for element in node.elts:
            self.visit(element)
            list_len += 1
        current_list = self.stack[-list_len:]
        self.stack = self.stack[:-list_len]
        self.stack.append(current_list)

    def visit_Name(self, node):
        if node.id in POKEMON_TYPES:
            self.stack.append(node.id)

    def eval(self, node: ast.AST | str) -> EvalResult:
        self.stack = []

        if isinstance(node, str):
            node = ast.parse(node)
        elif not isinstance(node, ast.AST):
            raise TypeError("node must be an AST or a string")

        self.visit(node)

        return EvalResult(
            result=self.stack[0] if self.stack else None,
            stack=self.stack,
            effects=self.effects,
        )
