import random as pyrandom
from typing import Any, Callable

from .data import DEFAULT_POKEMON_TYPES, DEFAULT_TYPE_EFFECTIVENESS


class PokyMethod:
    """
    Poky语言内建方法
    """
    def __init__(
            self,
            pokemon_types: list[str] | None = None,
            type_effectiveness: dict[str, dict[str, float]] | None = None,
    ):
        if pokemon_types is None:
            self.pokemon_types = DEFAULT_POKEMON_TYPES
        else:
            self.pokemon_types = pokemon_types

        if type_effectiveness is None:
            self.type_effectiveness = DEFAULT_TYPE_EFFECTIVENESS
        else:
            self.type_effectiveness = type_effectiveness

    def random(self, args: list[Any]) -> Any:
        """
        random(): 随机函数

        参数列表中元素个数为1且为整型时，在区间[0, args[0]]中随机选择一个整数

        参数列表中元素个数为1且为列表时，随机选择列表中的一个元素

        参数列表中元素个数为2且均为整型时，在区间[args[0], args[1]]中随机选择一个整数

        :param args: 参数列表

        :return: 随机结果
        """
        if len(args) == 1:
            # 随机数，区间[0, args[0]]
            if isinstance(args[0], int):
                return pyrandom.randint(0, args[0])

            # 随机选择一个元素
            if isinstance(args[0], list):
                return pyrandom.choice(args[0])

        # 随机数，随机区间[args[0], args[1]]
        if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
            return pyrandom.randint(args[0], args[1])

        # 无效参数
        raise ValueError("Invalid arguments for random function")

    def pokemon_types(self, raw_list: list[str]) -> list[str]:
        """
        pokemon_types(): 用于展开宝可梦列表

        :param raw_list: 原始宝可梦列表

        :return: 展开后的宝可梦列表
        """
        result_types = set()
        excludes = set()

        for name in raw_list:
            exclude = name.startswith("!")
            current_type = name[1:] if exclude else name

            # 处理所有属性
            if current_type == "all":
                if exclude:
                    return []
                for t in self.pokemon_types:
                    if t not in excludes:
                        result_types.add(t)
                continue

            # 检查属性
            if current_type not in self.pokemon_types:
                raise ValueError(f"Invalid Pokemon type: {current_type}")

            # 处理排除属性
            if exclude:
                excludes.add(current_type)
                if current_type in result_types:
                    result_types.remove(current_type)
                continue

            # 处理包含属性
            if current_type not in excludes:
                result_types.add(name)

        return list(result_types)

    def calculate_effectiveness(self, attacker_type: str, defender_types: list[str]) -> float:
        """
        计算攻击方对防御方的属性克制效果

        :param attacker_type: 攻击方属性
        :param defender_types: 防御方属性列表

        :return: 属性克制效果
        """
        effectiveness = 1.0
        for defender_type in defender_types:
            effectiveness *= self.type_effectiveness[attacker_type][defender_type]
        return effectiveness

    def print(self, args: list[Any]) -> None:
        """
        print(): 打印函数

        :param args: 参数列表
        """
        print(*args)

    @staticmethod
    def get_method(name: str) -> Callable | None:
        if not name.startswith("_") and name in PokyMethod.__dict__:
            member = PokyMethod.__dict__[name]
            if isinstance(member, Callable):
                return member
        return None
