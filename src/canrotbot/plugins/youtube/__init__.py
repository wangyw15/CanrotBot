import typing

from nonebot import on_regex
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import UniMessage, Image, Text

from canrotbot.essentials.libraries import util
from .config import YoutubeConfig
from .youtube import (
    YOUTUBE_LINK_PATTERN,
    fetch_youtube_data,
    fetch_youtube_thumbnail,
    generate_youtube_message,
)

__plugin_meta__ = PluginMetadata(
    name="YouTube",
    description="获取 YouTube 链接指向的内容",
    usage="发送支持解析的链接会自动触发",
    config=YoutubeConfig,
)

youtube_link_handler = on_regex(YOUTUBE_LINK_PATTERN, block=True)


@youtube_link_handler.handle()
async def _(reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]):
    data = await fetch_youtube_data(reg[0])
    if data:
        msg = generate_youtube_message(data)
        final_msg = UniMessage()
        if await util.can_send_segment(Image):
            img_data = await fetch_youtube_thumbnail(data)
            if img_data:
                final_msg.append(Image(raw=img_data))
        final_msg.append(Text(msg))
        await youtube_link_handler.finish(await final_msg.export())
