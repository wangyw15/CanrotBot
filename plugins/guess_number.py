from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
import random

__plugin_meta__ = PluginMetadata(
    name='猜数字',
    description='roll 一个各位都不相等的数字（默认四位），若玩家猜的数中，存在 n 个目标中的数，则给出 nA 的提示，若玩家猜的四位数中，存在 m 个数位置与目标中的相同，则给出 mB 的提示，当猜测数与目标数完全相同时游戏结束。',
    usage='/<guess_number|guess-number|猜数字|猜数>',
    config=None
)

def generate_number(num_len: int) -> str:
    if num_len > 10:
        num_len = 10
    if num_len < 1:
        num_len = 1
    nums = [str(x) for x in range(10)]
    random.shuffle(nums)
    return ''.join(nums[:num_len])

GUESS_NUMBER = 'GUESS_NUMBER'

guess_number = on_command('guess_number', aliases={'guess-number', '猜数字', '猜数'}, block=True)
@guess_number.handle()
async def _(state: T_State, args: Message = CommandArg()):
    num_len = 4
    if msg := args.extract_plain_text():
        if msg.isdigit():
            num_len = int(msg)
    state[GUESS_NUMBER] = generate_number(num_len)
    await guess_number.send(f'开始一轮猜数游戏（{num_len} 位）')

@guess_number.got('guess')
async def _(state: T_State, guess: Message = Arg()):
    answer: str = state[GUESS_NUMBER]
    guess = guess.extract_plain_text()
    if guess == 'stop':
        await guess_number.finish(f'游戏结束，答案是{state[GUESS_NUMBER]}')
    elif guess == answer:
        await guess_number.finish(f'恭喜你猜对了！')
    elif not guess.isdigit():
        await guess_number.reject('你输入的不是数字')
    elif len(guess) != len(answer):
        await guess_number.reject(f'你输入的数字长度不是{len(answer)}')
    else:
        a = 0
        b = 0
        for i in range(len(guess)):
            if guess[i] in answer:
                a += 1
            if guess[i] == answer[i]:
                b += 1
        await guess_number.reject(f'{a}A{b}B')
