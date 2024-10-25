import random

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from canrotbot.essentials.libraries import user, economy

__plugin_meta__ = PluginMetadata(
    name="猜数字",
    description="roll 一个各位都不相等的数字（默认四位），"
    "若玩家猜的数中，存在 n 个目标中的数，则给出 nA 的提示，"
    "若玩家猜的四位数中，存在 m 个数位置与目标中的相同，则给出 mB 的提示，"
    "当猜测数与目标数完全相同时游戏结束。",
    usage="/<guess_number|guess-number|猜数字|猜数>",
    config=None,
)


def generate_number(num_len: int) -> str:
    if num_len > 10:
        num_len = 10
    if num_len < 1:
        num_len = 1
    nums = [str(x) for x in range(10)]
    random.shuffle(nums)
    return "".join(nums[:num_len])


_GUESS_NUMBER = "GUESS_NUMBER"
_GUESS_NUMBER_TURNS = "GUESS_NUMBER_TURNS"

guess_number = on_command(
    "guess_number", aliases={"guess-number", "猜数字", "猜数"}, block=True
)


@guess_number.handle()
async def _(state: T_State, args: Message = CommandArg()):
    num_len = 4
    if msg := args.extract_plain_text():
        if msg.isdigit():
            num_len = int(msg)
    state[_GUESS_NUMBER] = generate_number(num_len)
    state[_GUESS_NUMBER_TURNS] = 0
    await guess_number.send(f"又来挑战{len(state[_GUESS_NUMBER])}位的猜数游戏了吗~")


@guess_number.got("guess")
async def _(state: T_State, guess: Message = Arg()):
    answer: str = state[_GUESS_NUMBER]
    guess = guess.extract_plain_text()
    if (
        guess == "stop"
        or guess == "停止"
        or guess == "停止游戏"
        or guess == "结束"
        or guess == "结束游戏"
    ):
        await guess_number.finish(
            f"答案是{state[_GUESS_NUMBER]}\n嗯...才{state[_GUESS_NUMBER_TURNS]}轮就放弃了啊..."
        )
    elif guess == answer:
        state[_GUESS_NUMBER_TURNS] += 1
        point_amounts = len(answer) * 10 - 2 * (int(state[_GUESS_NUMBER_TURNS]) - 8)
        economy.earn(user.get_uid(), point_amounts)
        await guess_number.finish(
            f"居然{state[_GUESS_NUMBER_TURNS]}轮就让你猜出来了。哼，{point_amounts}个胡萝卜片拿去"
        )
    elif not guess.isdigit():
        await guess_number.reject("你输入的不是数字喵~")
    elif len(guess) != len(answer):
        await guess_number.reject(f"是{len(answer)}位喵~")
    elif len(set(guess)) != len(answer):
        await guess_number.reject(f"是{len(answer)}位各位都不相同的数字喵~")
    else:
        state[_GUESS_NUMBER_TURNS] += 1
        a = 0
        b = 0
        for i in range(len(guess)):
            if guess[i] in answer:
                a += 1
            if guess[i] == answer[i]:
                b += 1
        await guess_number.reject(f"{a}A{b}B")
