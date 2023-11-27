import re

from arclet.alconna import Alconna, Option, Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Query, AlconnaQuery

from . import hitokoto

__plugin_meta__ = PluginMetadata(
    name="一言",
    description="随机一条一言",
    usage="/<hitokoto|一言> [一言分类，默认abc；或者uuid]\n分类详情查看发送 /一言 分类",
    config=None,
)


_command = on_alconna(
    Alconna(
        "一言",
        Args["query", str, ""],
        Option(
            "category",
            alias=["分类", "categories"],
        ),
    ),
    block=True,
)


@_command.assign("category")
async def _():
    ret_msg = []
    for category in hitokoto.get_categories():
        ret_msg.append(f'{category["key"]} - category["name"]')
        # ret_msg.append(f'名称: {category["name"]}\n描述: {category["desc"]}\n分类: {category["key"]}')
    await _command.finish("\n".join(ret_msg))


@_command.handle()
async def _(query: Query[str] = AlconnaQuery("query", "")):
    query = query.result.strip()
    categories = "abc"
    data: dict = {}
    if re.match(r"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}", query):
        data = hitokoto.get_hitokoto_by_uuid(query)
    else:
        categories = query
    if not data:
        data = hitokoto.random_hitokoto(categories)
    ret_msg = (
        f'{data["hitokoto"]}\n'
        f'-- {"" if not data["from_who"] else data["from_who"]}「{data["from"]}」\n'
        f'https://hitokoto.cn/?uuid={data["uuid"]}'
    )
    await _command.finish(ret_msg)
