from typing import Literal

from nonebot.adapters import Message
from nonebot.params import Arg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    Query,
    Subcommand,
    on_alconna,
)

from . import type_challenge

pokemon_command = Alconna(
    "pokemon",
    Subcommand(
        "type_challenge",
        Args["ptc_mode", str, "1"],
        alias=["属性挑战", "ptc"],
        help_text="开始属性挑战小游戏",
    ),
    Subcommand(
        "help",
        alias=["帮助"],
        help_text="获取帮助信息",
    ),
    meta=CommandMeta(description="提供宝可梦相关功能"),
)

__plugin_meta__ = PluginMetadata(
    name="宝可梦",
    description=pokemon_command.meta.description,
    usage=pokemon_command.get_help(),
    config=None,
)

pokemon_command_matcher = on_alconna(pokemon_command, aliases={"宝可梦"}, block=True)
ptc_matcher = pokemon_command_matcher.dispatch("type_challenge")
# ptc_matcher = pokemon_command_matcher


@pokemon_command_matcher.handle()
@pokemon_command_matcher.assign("help")
async def _():
    await pokemon_command_matcher.finish(pokemon_command.get_help())


# Type challenge game
ATTACK = "attack"
GUESS = "guess"
ROUND = "round"
TYPES = "types"
MAX_ROUNDS = 15


@ptc_matcher.handle()
# @ptc_matcher.assign("type_challenge")
async def ptc_start(
    state: T_State,
    ptc_mode: Query[Literal["1", "2", "random"]] = Query("ptc_mode", "1"),
):
    if ptc_mode.result not in ["1", "2", "random"]:
        await ptc_matcher.finish("无效的模式，请选择1, 2或random")

    state[ROUND] = 0
    state[TYPES] = type_challenge.generate_pokemon(ptc_mode.result)
    await ptc_matcher.send("宝可梦属性黑箱挑战，开始！")


@ptc_matcher.got("action_msg")
async def ptc_action(state: T_State, action_msg: Message = Arg()):
    if state[ROUND] == MAX_ROUNDS:
        await ptc_matcher.send(f"回合次数耗尽！正确属性：{'+'.join(state[TYPES])}")

    action_str = action_msg.extract_plain_text()

    # 设置动作和动作内容
    action = ""
    action_targets: list[str] = action_str.split()
    if action_str.startswith("a"):
        action = ATTACK
        action_targets = action_str[1:].split()
        for target in action_targets:
            if not type_challenge.check_type(target):
                await ptc_matcher.reject_arg(
                    "action_msg", f"无效的攻击属性：{action_targets}"
                )
    elif type_challenge.check_move(action_str):
        action = ATTACK
    elif type_challenge.check_type(action_str):
        action = GUESS
    else:
        await ptc_matcher.reject_arg(
            "action_msg", f"无效的攻击技能或属性：{action_str}"
        )

    # 执行动作
    if action == ATTACK:
        attack_type = type_challenge.get_move_type(action_targets[0])
        multiplier = type_challenge.calculate_effectiveness(attack_type, state[TYPES])
        prompt = type_challenge.get_effectiveness_prompt(multiplier)
        await ptc_matcher.send(prompt)
    elif action == GUESS:
        if sorted(action_targets) in state[TYPES]:
            await ptc_matcher.finish(
                f"恭喜你猜对了！正确属性：{'+'.join(state[TYPES])}"
            )
        else:
            await ptc_matcher.reject_arg("action_msg", "猜测错误")

    state[ROUND] += 1
