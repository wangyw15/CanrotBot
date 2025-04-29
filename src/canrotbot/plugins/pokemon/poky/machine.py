import ast
from typing import Callable

from .data import DEFAULT_POKEMON_TYPES, DEFAULT_TYPE_EFFECTIVENESS
from .methods import PokyMethod
from .model import Effects, EvalResult


class PokyMachine(ast.NodeVisitor):
    """
    运行Poky语言
    """

    PERSISTENT = "persistent"
    RUNTIME = "runtime"
    STORAGE = "storage"
    ENVIRONMENT = "environment"

    stack: list = []
    persistent_storage: dict = {}
    runtime_storage: dict = {}
    persistent_environment: dict = {}
    runtime_environment: dict = {}
    effects: Effects = {}

    def __init__(
        self,
        pokemon_types: list[str] | None = None,
        type_effectiveness: dict[str, dict[str, float]] | None = None,
        persistent_environment: dict | None = None,
    ):
        """
        初始化Poky语言运行环境

        :param pokemon_types: 宝可梦属性列表
        :param type_effectiveness: 宝可梦属性克制效果
        :param persistent_environment: 持久化环境
        """
        if pokemon_types is None:
            self.pokemon_types = DEFAULT_POKEMON_TYPES
        else:
            self.pokemon_types = pokemon_types

        if type_effectiveness is None:
            self.type_effectiveness = DEFAULT_TYPE_EFFECTIVENESS
        else:
            self.type_effectiveness = type_effectiveness

        if persistent_environment is None:
            self.persistent_environment = {}
        else:
            self.persistent_environment = persistent_environment

        self.builtin_methods = PokyMethod(self.pokemon_types, self.type_effectiveness)

    def reset(self, reset_persistent: bool = False):
        """
        重置Poky语言运行环境

        :param reset_persistent: 是否重置持久化内容
        """
        self.stack = []
        self.runtime_storage = {}
        self.runtime_environment = {}
        self.effects = {}

        if reset_persistent:
            self.persistent_environment = {}
            self.persistent_storage = {}

    def eval(self, node: ast.AST | str, runtime_environment: dict | None = None) -> EvalResult:
        """
        运行Poky语言

        :param node: AST节点或字符串
        :param runtime_environment: 运行时环境变量，不传入则为空

        :return: 运行结果
        """
        if isinstance(node, str):
            node = ast.parse(node)
        elif not isinstance(node, ast.AST):
            raise TypeError("node must be an AST or a string")

        # 重置环境
        self.reset()
        if runtime_environment is None:
            self.runtime_environment = {}
        else:
            self.runtime_environment = runtime_environment

        self.visit(node)

        return EvalResult(
            result=self.stack[0] if self.stack else None,
            stack=self.stack,
            effects=self.effects,
        )

    # 内建效果类函数
    def effect_change_effectiveness(self, args: list):
        self.effects["effectiveness"] = args[0]

    # 运行Poky语言
    # 处理二元运算符
    def visit_BinOp(self, node):
        self.generic_visit(node)

        right = self.stack.pop()
        operator = self.stack.pop()
        left = self.stack.pop()

        if isinstance(left, (int, float, complex)) and isinstance(
            right, (int, float, complex)
        ):
            self.stack.append(type(left).__dict__[operator](left, right))

        elif isinstance(left, str) and isinstance(right, str):
            if left in self.pokemon_types and right in self.pokemon_types:
                if operator == int.__pow__.__name__:
                    self.stack.append(
                        PokyMethod.calculate_effectiveness(self.builtin_methods, left, [right])
                    )
                elif operator == int.__add__.__name__:
                    self.stack.append([left, right])
                else:
                    raise TypeError("unsupported operand between pokemon types")
            elif operator == int.__add__.__name__:
                self.stack.append(left + right)
            else:
                raise TypeError("Unsupported operator")

        elif operator == int.__add__.__name__ and (
            isinstance(left, list) or isinstance(right, list)
        ):
            if isinstance(left, list) and not isinstance(right, list):
                self.stack.append(left + [right])
            elif not isinstance(left, list) and isinstance(right, list):
                self.stack.append([left] + right)
            else:
                self.stack.append(left + right)

        else:
            raise TypeError("Unsupported operator")

    def visit_Add(self, node):
        self.generic_visit(node)
        self.stack.append(int.__add__.__name__)

    def visit_Sub(self, node):
        self.generic_visit(node)
        self.stack.append(int.__sub__.__name__)

    def visit_Mult(self, node):
        self.generic_visit(node)
        self.stack.append(int.__mul__.__name__)

    def visit_Div(self, node):
        self.generic_visit(node)
        self.stack.append(int.__truediv__.__name__)

    def visit_Mod(self, node):
        self.generic_visit(node)
        self.stack.append(int.__mod__.__name__)

    def visit_FloorDiv(self, node):
        self.generic_visit(node)
        self.stack.append(int.__floordiv__.__name__)

    def visit_BitAnd(self, node):
        self.generic_visit(node)
        self.stack.append(int.__and__.__name__)

    def visit_Pow(self, node):
        self.generic_visit(node)
        self.stack.append(int.__pow__.__name__)

    def visit_Attribute(self, node):
        self.generic_visit(node)

        if isinstance(node.ctx, ast.Load):
            arg = self.stack.pop()
            if isinstance(arg, dict):
                if node.attr in arg:
                    self.stack.append(arg[node.attr])
                else:
                    if arg is self.persistent_storage or arg is self.runtime_storage:
                        self.stack.append(None)
                    else:
                        raise SyntaxError(f"Invalid attribute: {node.attr}")
            elif hasattr(arg, "__dict__") and node.attr in arg.__dict__:
                self.stack.append(arg.__dict__[node.attr])
            else:
                raise SyntaxError(f"Invalid attribute: {node.attr}")
        elif isinstance(node.ctx, ast.Store):
            self.stack.append(node.attr)

    def visit_Constant(self, node):
        self.generic_visit(node)
        self.stack.append(node.value)

    def visit_Call(self, node):
        self.generic_visit(node)

        args = self.stack[-len(node.args):]
        self.stack = self.stack[:-len(node.args)]
        func = self.stack.pop()

        if func.__qualname__.split(".")[-2] == PokyMachine.__name__:
            self.stack.append(func(self, args))
        else:
            self.stack.append(func(self.builtin_methods, args))

    def visit_List(self, node):
        self.generic_visit(node)

        elements = self.stack[-len(node.elts):]
        self.stack = self.stack[:-len(node.elts)]
        self.stack.append(elements)

    def visit_Name(self, node):
        self.generic_visit(node)

        if isinstance(node.ctx, ast.Load):
            if ("effect_" + node.id in PokyMachine.__dict__
                    and isinstance(PokyMachine.__dict__["effect_" + node.id], Callable)):
                self.stack.append(PokyMachine.__dict__["effect_" + node.id])
            elif builtin_method := PokyMethod.get_method(node.id):
                self.stack.append(builtin_method)
            elif node.id in self.runtime_environment:
                self.stack.append(self.runtime_environment[node.id])
            elif node.id in self.persistent_environment:
                self.stack.append(self.persistent_environment[node.id])
            elif node.id in self.pokemon_types:
                self.stack.append(node.id)
            elif node.id == self.PERSISTENT:
                self.stack.append(self.persistent_storage)
            elif node.id == self.RUNTIME:
                self.stack.append(self.runtime_storage)
            else:
                raise NameError(f"Invalid name: {node.id}")
        elif isinstance(node.ctx, ast.Store):
            self.stack.append(node.id)

    def visit_If(self, node):
        if isinstance(node.test, ast.Constant) and isinstance(node.test.value, bool):
            self.stack.append(node.test.value)
        elif not isinstance(node.test, ast.Compare):
            raise SyntaxError("Invalid if statement")

        self.visit(node.test)
        if self.stack.pop():
            for expr in node.body:
                self.visit(expr)
        else:
            for expr in node.orelse:
                self.visit(expr)

    def visit_Compare(self, node):
        self.generic_visit(node)

        operator = node.ops[0]
        right = self.stack.pop()
        left = self.stack.pop()
        if isinstance(operator, ast.Eq):
            self.stack.append(left == right)
        if isinstance(operator, ast.NotEq):
            self.stack.append(left != right)
        elif isinstance(operator, ast.Is):
            self.stack.append(left is right)
        elif isinstance(operator, ast.IsNot):
            self.stack.append(left is not right)
        else:
            raise SyntaxError(f"Invalid comparison operator: {node.ops}")

    def visit_Assign(self, node):
        self.generic_visit(node)

        value = self.stack.pop()
        name = self.stack.pop()
        storage = self.stack.pop()

        storage[name] = value


    def visit_IfExp(self, node):
        if isinstance(node.test, ast.Constant) and isinstance(node.test.value, bool):
            self.stack.append(node.test.value)
        elif not isinstance(node.test, ast.Compare):
            raise SyntaxError("Invalid ifexp statement")

        self.visit(node.test)
        if self.stack.pop():
            self.visit(node.body)
        else:
            self.visit(node.orelse)
