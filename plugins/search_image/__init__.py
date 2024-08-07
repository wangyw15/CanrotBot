import nonebot.adapters.kaiheila as kook
from arclet.alconna import Args
from nonebot.adapters import Bot
from nonebot.params import Arg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    AlconnaQuery,
    Query,
    UniMessage,
    UniMsg,
    Image,
)

from essentials.libraries import util
from . import search_image
from .config import SearchImageConfig

__plugin_meta__ = PluginMetadata(
    name="识图",
    description="通过 SauceNAO.com 或者 trace.moe 识图，目前仅支持QQ直接发送图片搜索",
    usage="先发送/<识图|搜图>，再发图片或者图片链接\n可选择搜图 API:\ntracemoe (trace.moe) 只能搜番剧\nsaucenao (saucenao.com) 默认",
    config=SearchImageConfig,
)


_search_image = on_alconna(Alconna("搜图", Args["api", str, "saucenao"]), block=True)


@_search_image.handle()
async def _(
    state: T_State, bot: Bot, api: Query[str] = AlconnaQuery("api", "saucenao")
):
    api = api.result.strip().lower()
    if api not in ["saucenao", "tracemoe"]:
        await _search_image.finish("无效的搜图网站选项")
    state["SEARCH_IMAGE_API"] = api

    if util.is_qq(bot) or isinstance(bot, kook.Bot):
        await _search_image.send("请发送图片或图片链接")
    else:
        await _search_image.send("请发送图片链接")


@_search_image.got("image_msg")
async def _(state: T_State, image_msg: UniMsg = Arg()):
    # get img url
    if image_msg[0].type == Image.__name__:
        img_url = image_msg[0].data["url"].strip()
    else:
        img_url = image_msg.extract_plain_text().strip()

    # search
    if img_url and (img_url.startswith("https://") or img_url.startswith("http://")):
        msg = UniMessage()
        api: str = state["SEARCH_IMAGE_API"]
        if api == "saucenao":
            search_resp = await search_image.search_image_from_saucenao(img_url)
            if search_resp:
                msg = await search_image.generate_message_from_saucenao_result(
                    search_resp
                )
            else:
                await _search_image.finish("搜索失败")
        elif api == "tracemoe":
            search_resp = await search_image.search_image_from_tracemoe(img_url)
            if search_resp:
                msg = await search_image.generate_message_from_tracemoe_result(
                    search_resp
                )
            else:
                await _search_image.finish("搜索失败")
        await _search_image.finish(msg)
    else:
        await _search_image.finish("图片链接错误，停止搜图")
