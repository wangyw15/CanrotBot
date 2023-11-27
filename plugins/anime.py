from arclet.alconna import Option, Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    AlconnaQuery,
    Query,
    UniMsg,
    Text,
    Image,
)

from essentials.libraries import util
from libraries import anime

__plugin_meta__ = PluginMetadata(
    name="番剧工具",
    description="是个提供番剧相关的插件，但是现在只提供番剧搜索功能",
    usage="/<anime|番剧|动漫> <搜索> <关键词>",
    config=None,
)


def generate_message_from_anime_data(name: str, data: dict, possibility: float) -> str:
    # 放送状态
    anime_status = "未知"
    if data["status"] == "FINISHED":
        anime_status = "完结"
    elif data["status"] == "ONGOING":
        anime_status = "更新中"
    elif data["status"] == "UPCOMING":
        anime_status = "待放送"
    # 春夏秋冬季
    anime_time = f'{data["animeSeason"]["year"]}年'
    if data["animeSeason"]["season"] == "SPRING":
        anime_time += "春季"
    elif data["animeSeason"]["season"] == "SUMMER":
        anime_time += "夏季"
    elif data["animeSeason"]["season"] == "FALL":
        anime_time += "秋季"
    elif data["animeSeason"]["season"] == "WINTER":
        anime_time += "冬季"
    # 生成消息
    msg = (
        f'标题: {name if name else data["title"]}\n'
        f'类型: {data["type"]}\n'
        f'共 {data["episodes"]} 集\n'
        f"状态: {anime_status}\n"
        f"时间: {anime_time}\n"
        f'标签: {", ".join(data["tags"])}\n'
        f"匹配度: {possibility * 100:.2f}%"
    )
    return msg


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
async def _(anime_query: Query[str] = AlconnaQuery("anime_query")):
    name, data, possibility = anime.search_anime_by_name(anime_query.result.strip())
    text_msg = generate_message_from_anime_data(name, data, possibility)
    msg = UniMsg()
    if await util.can_send_segment(Image):
        msg.append(Image(url=data["picture"]))
    msg.append(Text(text_msg))
    await _command.finish(msg)


@_command.handle()
async def _():
    await _command.finish(__plugin_meta__.usage)
