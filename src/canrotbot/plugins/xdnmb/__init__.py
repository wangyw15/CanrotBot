import typing

from arclet.alconna import Args
from nonebot import on_regex
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    AlconnaQuery,
    Query,
    UniMessage,
    Text,
)

from . import xdnmb

__plugin_meta__ = PluginMetadata(
    name="xdnmb",
    description="自动获取串号内容",
    usage="发送链接或者/xd <串号>",
    config=None,
)
# TODO 设置饼干用于查看


async def _generate_message(thread_number: str) -> UniMessage | None:
    if data := await xdnmb.get_thread_data(thread_number):
        msg = UniMessage()
        msg += xdnmb.generate_message(data, True)
        for i in range(3):
            msg.append(Text("--------------------\n"))
            msg += xdnmb.generate_message(data["Replies"][i])
            msg.append(Text("\n"))
        return msg
    return None


_command = on_alconna(
    Alconna(
        "xdnmb",
        Args["thread_number", str],
    ),
    block=True,
)
_xd_link_handler = on_regex(
    r"(?:https?:\/\/)?(?:www\.)?nmbxd.com\/t\/(\d+)", block=True
)


@_command.handle()
async def _(thread_number: Query[str] = AlconnaQuery("thread_number")):
    thread_number = thread_number.result.strip()
    if thread_number.isdigit():
        if msg := await _generate_message(thread_number):
            await _command.finish(msg)
    await _command.finish("未找到该串号")


@_command.handle()
async def _():
    await _command.finish(__plugin_meta__.usage)


@_xd_link_handler.handle()
async def _(reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]):
    if msg := await _generate_message(reg[0]):
        await _command.finish(await msg.export())
    await _command.finish("未找到该串号")
