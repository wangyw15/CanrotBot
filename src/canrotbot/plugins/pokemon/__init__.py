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
        Args["ptc_mode?", Literal["1", "2", "random"], "1"],
        alias=["属性挑战", "ptc"],
        help_text="宝可梦属性黑箱挑战小游戏",
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

pokemon_command_matcher = on_alconna(
    pokemon_command, aliases={"宝可梦"}, auto_send_output=False
)


@pokemon_command_matcher.assign("help")
async def _():
    await pokemon_command_matcher.finish(pokemon_command.get_help())


# 黑箱属性游戏
ptc_matcher = pokemon_command_matcher.dispatch("type_challenge")

ATTACK = "attack"
GUESS = "guess"
ROUND = "round"
TYPES = "types"
GIVE_UP = ["逃跑", "放弃"]
MAX_ROUNDS = 15


@ptc_matcher.handle()
async def ptc_start(
    state: T_State,
    ptc_mode: Query[Literal["1", "2", "random"]] = Query("ptc_mode", "1"),
):
    if ptc_mode.result not in ["1", "2", "random"]:
        await ptc_matcher.finish("无效的模式，请选择1, 2或random")

    state[ROUND] = 0
    state[TYPES] = type_challenge.generate_pokemon(ptc_mode.result)
    await ptc_matcher.send(
        "宝可梦属性黑箱挑战，开始！\n"
        + f"当前是【{'单一' if len(state[TYPES]) == 1 else '双'}】属性模式\n"
        + "输入【a属性】或【技能名称】进行攻击\n"
        + "输入【属性】进行猜测\n"
        + "输入【放弃】或【逃跑】放弃游戏"
    )
    from nonebot import logger

    logger.error(state[TYPES])


@ptc_matcher.got("action_msg")
async def ptc_action(state: T_State, action_msg: Message = Arg()):
    if state[ROUND] == MAX_ROUNDS:
        await ptc_matcher.finish(
            f"回合数耗尽了……宝可梦黑箱逃跑了！\n正确答案是【{'+'.join(state[TYPES])}】"
        )

    action_str = action_msg.extract_plain_text()

    # 检查是否逃跑
    if action_str in GIVE_UP:
        await ptc_matcher.finish(
            f"玩家从宝可梦属性黑箱挑战中逃跑了！\n正确答案是【{'+'.join(state[TYPES])}】"
        )

    # 检查并设置动作和动作内容
    action = ""
    action_targets: list[str] = action_str.split()
    type_count = len(state[TYPES])
    target_count = len(action_targets)
    if action_str.startswith("a"):
        action = ATTACK
        action_targets = action_str[1:].split()
        if target_count != 1:
            await ptc_matcher.reject_arg("action_msg", "请输入一个攻击技能或属性")
        if not type_challenge.check_type(action_targets[0]):
            if not type_challenge.check_move(action_targets[0]):
                await ptc_matcher.reject_arg(
                    "action_msg", f"无效的攻击技能或属性：{action_targets[0]}"
                )
    else:
        if target_count == 1:
            if type_challenge.check_move(action_targets[0]):
                action = ATTACK
            elif type_challenge.check_type(action_targets[0]):
                action = GUESS if type_count == 1 else ATTACK
            else:
                await ptc_matcher.reject_arg(
                    "action_msg", f"无效的攻击技能或属性：{action_str}"
                )
        else:
            # 多个target只能为猜测属性
            action = GUESS

            # 单一属性模式只能猜测一个属性
            if type_count == 1:
                await ptc_matcher.reject_arg(
                    "action_msg", "单一属性模式下只能猜测一个属性"
                )

            # 检查属性是否有效
            for i in action_targets:
                if not type_challenge.check_type(i):
                    await ptc_matcher.reject_arg("action_msg", f"无效的属性猜测：{i}")

    # 更新回合数
    state[ROUND] += 1

    # 执行动作
    if action == ATTACK:
        if type_challenge.check_move(action_targets[0]):
            attack_type = type_challenge.get_move_type(action_targets[0])
        else:
            attack_type = action_targets[0]

        multiplier = type_challenge.calculate_effectiveness(attack_type, state[TYPES])
        prompt = type_challenge.get_effectiveness_prompt(multiplier)
        await ptc_matcher.reject_arg(
            "action_msg",
            f"【{attack_type}】属性攻击！\n"
            + f"{prompt}\n"
            + f"剩余回合数：{MAX_ROUNDS - state[ROUND]}/{MAX_ROUNDS}",
        )
    elif action == GUESS:
        if sorted(action_targets) == sorted(state[TYPES]):
            await ptc_matcher.finish(
                f"恭喜你，正确答案是【{'+'.join(state[TYPES])}】！"
            )
        else:
            await ptc_matcher.reject_arg(
                "action_msg",
                "很遗憾，回答错误，再多尝试几次吧。\n"
                + f"剩余回合数：{MAX_ROUNDS - state[ROUND]}/{MAX_ROUNDS}",
            )
