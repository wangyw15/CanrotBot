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
    calculated_expr = ''
    simple_exp = ''
    for c in expr:
        if c.isdigit() or c in ['d']:
            simple_exp += c
        else:
            if simple_exp:
                calculated_expr += str(simple_dice_expression(simple_exp))
                simple_exp = ''
            calculated_expr += c
    if simple_exp:
        calculated_expr += str(simple_dice_expression(simple_exp))
    return eval(calculated_expr), calculated_expr


def main():
    while True:
        command = input('> ')
        if command == 'exit':
            break
        print(dice_expression(command))


if __name__ == '__main__':
    main()
