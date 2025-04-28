import random as pyrandom
from typing import Any

from .data import POKEMON_TYPES


class PokyMethods:
    @staticmethod
    def random(args: list[Any]) -> Any:
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

    @staticmethod
    def pokemon_types(raw_list: list[str]) -> list[str]:
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
                for t in POKEMON_TYPES:
                    if t not in excludes:
                        result_types.add(t)
                continue

            # 检查属性
            if current_type not in POKEMON_TYPES:
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
