from nonebot import get_plugin_config, on_message
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    Match,
    MsgTarget,
    Subcommand,
    UniMsg,
    on_alconna,
)

from . import reply
from .config import ReplyConfig
from .model import ReplyMode

reply_command = Alconna(
    "reply",
    Subcommand(
        "rate",
        Args["new_rate?", float],
        alias=["概率"],
        help_text="获取或设置自动回复概率",
    ),
    Subcommand(
        "mode",
        Args["new_mode?", str],
        alias=["模式"],
        help_text="获取或设置自动回复模式",
    ),
    meta=CommandMeta(description="自动回复，附赠自动水群功能，概率触发机器人自动回复"),
)

__plugin_meta__ = PluginMetadata(
    name="自动回复",
    description=reply_command.meta.description,
    usage=reply_command.get_help(),
    config=ReplyConfig,
)

config = get_plugin_config(ReplyConfig)

message_matcher = on_message(rule=reply.check_reply, priority=101, block=True)
reply_command_matcher = on_alconna(reply_command, aliases={"自动回复"}, block=True)


@message_matcher.handle()
async def _(target: MsgTarget, msg: UniMsg):
    """
    处理自动回复
    """
    response = reply.get_response(
        msg.extract_plain_text(), reply.get_reply_mode(target)
    )
    if response:
        await message_matcher.finish(response)
    else:
        await message_matcher.finish()


@reply_command_matcher.assign("rate")
async def _(target: MsgTarget, new_rate: Match[float]):
    """
    获取或设置自动回复概率
    """
    if new_rate.available:
        if new_rate.result < 0 or new_rate.result > 1:
            await reply_command_matcher.finish("概率范围应为0-1")
        reply.set_reply_rate(target, new_rate.result)
        await reply_command_matcher.finish(
            f"自动回复概率已设置为{new_rate.result}，请注意不要设置过高喵~"
        )
    else:
        await reply_command_matcher.finish(
            f"当前自动回复概率为{reply.get_reply_rate(target)}"
        )


@reply_command_matcher.assign("mode")
async def _(target: MsgTarget, new_mode: Match[str]):
    """
    获取或设置自动回复模式
    """
    if new_mode.available:
        if new_mode.result not in ReplyMode:
            await reply_command_matcher.finish(
                "模式不存在，可用模式有：\n"
                + "\n".join([mode.value for mode in ReplyMode])
            )
        reply.set_reply_mode(target, ReplyMode(new_mode.result))
        await reply_command_matcher.finish(f"自动回复模式已设置为{new_mode.result}")
    else:
        await reply_command_matcher.finish(
            f"当前自动回复模式为{reply.get_reply_mode(target).value}"
        )


@reply_command_matcher.handle()
async def _():
    """
    返回帮助信息
    """
    await reply_command_matcher.finish(reply_command.get_help())
