import typing

from nonebot import on_regex
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata

from canrotbot.essentials.libraries.util import get_file_message

from . import line_sticker

__plugin_meta__ = PluginMetadata(
    name="Line 表情包下载",
    description="下载 Line 表情包",
    usage="发送链接就可以触发",
    config=None,
)


line_sticker_link_matcher = on_regex(
    r"(?:https?:\/\/)?store\.line\.me\/stickershop\/product\/(\d+)", block=True
)


@line_sticker_link_matcher.handle()
async def _(reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]):
    sticker_id = reg[0].strip()
    name, content = await line_sticker.get_line_sticker(sticker_id)
    await line_sticker_link_matcher.finish(
        await get_file_message(name + ".zip", content)
    )
