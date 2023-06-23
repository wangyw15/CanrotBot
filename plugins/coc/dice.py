import random


def simple_dice(a: int, b: int) -> int:
    """
    最简单的骰子，包含最小值和最大值

    :param a: 最小值
    :param b: 最大值
    """
    return random.randint(a, b)


def simple_dice_command(command: str) -> int:
    """
    简单骰子指令，如1d10，2d6，d100

    :param command: 骰子指令
    """
    if command.isdigit():
        return int(command)
    command = command.lower()
    # 不指定次数
    if command.startswith('d'):
        return simple_dice(1, int(command[1:]))
    # 指定次数
    nums = [int(x) for x in command.split('d')]
    return sum(simple_dice(1, nums[1]) for _ in range(nums[0]))


def dice_command(command: str) -> int:
    """
    复杂骰子指令，如d10+1+2d6

    :param command: 骰子指令
    """
    command = command.lower()
    return sum(simple_dice_command(x) for x in command.split('+'))


def main():
    while True:
        command = input('> ')
        if command == 'exit':
            break
        print(dice_command(command))


if __name__ == '__main__':
    main()
