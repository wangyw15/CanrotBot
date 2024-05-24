import typing

from nonebot import on_regex
from nonebot.adapters import Bot, Event
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import File, UniMessage

from essentials.libraries import util
from . import line_sticker

__plugin_meta__ = PluginMetadata(
    name="Line 表情包下载",
    description="下载 Line 表情包",
    usage="发送链接就可以触发",
    config=None,
)


_line_sticker_handler = on_regex(
    r"(?:https?:\/\/)?store\.line\.me\/stickershop\/product\/(\d+)", block=True
)


@_line_sticker_handler.handle()
async def _(
    bot: Bot, event: Event, reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]
):
    if not await util.can_send_segment(File):
        await _line_sticker_handler.finish()
    sticker_id = reg[0].strip()
    name, content = await line_sticker.get_line_sticker(sticker_id)
    await line_sticker.send_file(content, name + ".zip", bot, event)
    await _line_sticker_handler.finish(
        await UniMessage(File(raw=content, name=name + ".zip")).export()
    )
