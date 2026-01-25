import random

from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    Image,
    Query,
    Subcommand,
    on_alconna,
)

from canrotbot.essentials.libraries import util

from . import waifu

waifu_command = Alconna(
    "waifu",
    Subcommand(
        "list_category",
        alias=["分类", "分类列表", "查看分类", "list"],
        help_text="显示所有可用的分类",
    ),
    Args["category", str, "random"],
    meta=CommandMeta(description="随机 roll 老婆"),
)

__plugin_meta__ = PluginMetadata(
    name="waifu",
    description=waifu_command.meta.description,
    usage=waifu_command.get_help(),
    config=None,
)


waifu_matcher = on_alconna(
    waifu_command,
    aliases={"老婆", "纸片人"},
    block=True,
)


@waifu_matcher.assign("list_category")
async def _():
    await waifu_matcher.finish(f"可选类型：\n{', '.join(waifu.AVAILABLE_CATEGORY)}")


@waifu_matcher.handle()
async def _(category: Query[str] = Query("category", "random")):
    if not await util.can_send_segment(Image):
        await waifu_matcher.finish("这里不能发送图片喵~")

    selected_category = category.result.strip().lower()
    if selected_category == "random":
        selected_category = random.choice(waifu.AVAILABLE_CATEGORY)
    if selected_category not in waifu.AVAILABLE_CATEGORY:
        await waifu_matcher.finish("没有这个类型哦")

    img_url = await waifu.get_waifu_url("sfw", selected_category)
    if img_url:
        await waifu_matcher.finish(Image(url=img_url))
    else:
        await waifu_matcher.finish("获取图片失败")
