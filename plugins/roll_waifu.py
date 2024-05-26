import random

import httpx
from arclet.alconna import Option, Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Alconna, AlconnaQuery, Query, Image

from essentials.libraries import user, economy, util

__plugin_meta__ = PluginMetadata(
    name="waifu",
    description="随机 roll 老婆",
    usage="/<waifu|老婆|纸片人> [类型，默认随机]",
    config=None,
)

_client = httpx.AsyncClient()
api_url = "https://api.waifu.pics/{type}/{category}"
categories = [
    "waifu",
    "neko",
    "shinobu",
    "megumin",
    "bully",
    "cuddle",
    "cry",
    "hug",
    "awoo",
    "kiss",
    "lick",
    "pat",
    "smug",
    "bonk",
    "yeet",
    "blush",
    "smile",
    "wave",
    "highfive",
    "handhold",
    "nom",
    "bite",
    "glomp",
    "slap",
    "kill",
    "kick",
    "happy",
    "wink",
    "poke",
    "dance",
    "cringe",
]


async def get_waifu_url(image_type: str, category: str) -> str | None:
    resp = await _client.get(api_url.format(type=image_type, category=category))
    if resp.status_code == 200:
        return resp.json()["url"]
    return None


_command = on_alconna(
    Alconna(
        "waifu",
        Option(
            "list_category",
            alias=["分类", "分类列表", "查看分类", "list"],
        ),
        Args["category", str, "random"],
    ),
    aliases={"老婆", "纸片人"},
    block=True,
)


@_command.assign("list_category")
async def _():
    await _command.finish(f'可选类型：\n{", ".join(categories)}')


@_command.handle()
async def _(category: Query[str] = AlconnaQuery("category", "random")):
    if not await util.can_send_segment(Image):
        await _command.finish("这里不能发送图片喵~")

    category = category.result.strip().lower()
    if category == "random":
        category = random.choice(categories)
    if category not in categories:
        await _command.finish("没有这个类型哦")

    if not economy.pay(await user.get_uid(), 2, "随机 waifu"):
        await _command.finish("你的余额不足哦")

    await _command.send("谢谢你的两个胡萝卜片喵~\n正在找图哦~")
    img_url = await get_waifu_url("sfw", category)
    if img_url:
        await _command.finish(Image(url=img_url))
    else:
        await _command.finish("获取图片失败")
