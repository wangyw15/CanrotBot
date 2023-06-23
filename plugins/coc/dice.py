import random
import re
from typing import Tuple


def simple_dice(a: int, b: int) -> int:
    """
    最简单的骰子，包含最小值和最大值

    :param a: 最小值
    :param b: 最大值
    """
    return random.randint(a, b)


def simple_dice_expression(expr: str) -> int:
    """
    简单骰子表达式，如1d10，2d6，d100

    :param expr: 骰子表达式
    """
    if expr.isdigit():
        return int(expr)
    expr = expr.lower()
    # 不指定次数
    if expr.startswith('d'):
        return simple_dice(1, int(expr[1:]))
    # 指定次数
    nums = [int(x) for x in expr.split('d')]
    return sum(simple_dice(1, nums[1]) for _ in range(nums[0]))


def dice_expression(expr: str) -> Tuple[int, str]:
    """
    复杂骰子表达式，如d10+1+2d6

    :param expr: 骰子表达式
    """
    expr = expr.lower()
    expr_arr = list(expr)
    simple_seg: list[Tuple[Tuple, str]] = []  # 简单骰子表达式的位置和内容
    # 找出所有骰子表达式
    for i in re.finditer(r'((\d+)?[Dd](\d+)|\d+)', expr):
        simple_seg.append((i.span(), i.group()))
    simple_seg.reverse()  # 从后往前替换，避免替换后索引变化
    # 替换骰子表达式为数字
    for i in simple_seg:
        expr_arr[i[0][0]:i[0][1]] = [str(simple_dice_expression(i[1]))]
    calculated_expr = ''.join(expr_arr)  # 计算后的表达式
    return eval(calculated_expr), calculated_expr


def main():
    while True:
        command = input('> ')
        if command == 'exit':
            break
        print(dice_expression(command))


if __name__ == '__main__':
    main()
