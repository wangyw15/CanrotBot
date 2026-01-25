from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    Query,
    Subcommand,
    on_alconna,
)

from canrotbot.libraries import anilist, bangumi

from .anime import (
    generate_message_from_anilist_data,
    generate_message_from_bangumi_calendar,
)

anime_command = Alconna(
    "anime",
    Subcommand(
        "search",
        Args["anime_query", str],
        alias=["搜索", "查番", "番剧", "动漫"],
        help_text="搜索番剧并获取详细信息",
    ),
    Subcommand(
        "calendar",
        alias=["日历", "每日放送"],
        help_text="获取当前的每日放送",
    ),
    meta=CommandMeta(description="提供番剧相关的插件，例如搜索和每日放送日历"),
)

__plugin_meta__ = PluginMetadata(
    name="番剧工具",
    description=anime_command.meta.description,
    usage=anime_command.get_help(),
    config=None,
)

anime_matcher = on_alconna(
    anime_command,
    aliases={"动漫", "番剧"},
    block=True,
)


@anime_matcher.assign("search")
async def _(anime_query: Query[str] = Query("anime_query")):
    data = await anilist.search_anime_by_title(anime_query.result.strip())
    await anime_matcher.finish(generate_message_from_anilist_data(data))


@anime_matcher.assign("calendar")
async def _():
    data = await bangumi.get_airing_calendar()
    await anime_matcher.finish(generate_message_from_bangumi_calendar(data))
