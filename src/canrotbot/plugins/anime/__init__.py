from arclet.alconna import Args, Option
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Query,
    Text,
    UniMessage,
    on_alconna,
)

from canrotbot.libraries import anilist

from .anime import generate_message_from_anilist_data

__plugin_meta__ = PluginMetadata(
    name="番剧工具",
    description="是个提供番剧相关的插件，但是现在只提供番剧搜索功能",
    usage="/<anime|番剧|动漫> <搜索> <关键词>",
    config=None,
)


_command = on_alconna(
    Alconna(
        "anime",
        Option(
            "search",
            Args["anime_query", str],
            alias=["搜索", "查番", "番剧", "动漫"],
        ),
    ),
    aliases={"动漫", "番剧"},
    block=True,
)


@_command.assign("search")
async def _(anime_query: Query[str] = Query("anime_query")):
    data = await anilist.search_anime_by_title(anime_query.result.strip())
    text_msg = generate_message_from_anilist_data(data)
    msg = UniMessage()
    msg.append(Text(text_msg))
    await _command.finish(msg)
