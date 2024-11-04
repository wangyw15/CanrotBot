from nonebot import logger
from nonebot.adapters.qq import Bot as QQBot
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    Image,
    Match,
    Query,
    UniMessage,
    on_alconna,
)

from . import search_image
from .config import SearchImageConfig

SEARCH_IMAGE_API_FLAG = "SEARCH_IMAGE_API"
WITHOUT_URL_FLAG = "WITHOUT_URL"

search_image_command = Alconna(
    "search_image",
    Args["image?", Image]["api", str, "saucenao"],
    meta=CommandMeta(
        description="通过 SauceNAO.com 或者 trace.moe 识图，目前支持直接发送图片搜索"
    ),
)

__plugin_meta__ = PluginMetadata(
    name="识图",
    description=search_image_command.meta.description,
    usage="先发送/<识图|搜图>，再发图片\n可选择搜图 API:\ntracemoe (trace.moe) 只能搜番剧\nsaucenao (saucenao.com) 默认",
    config=SearchImageConfig,
)


search_image_matcher = on_alconna(
    search_image_command,
    aliases={"识图", "搜图"},
    block=True,
)


@search_image_matcher.handle()
async def _(state: T_State, api: Query[str] = Query("api", "saucenao")):
    api = api.result.strip().lower()
    if api not in search_image.AVAILABLE_API:
        await search_image_matcher.finish("无效的搜图网站选项")
    state[SEARCH_IMAGE_API_FLAG] = api


@search_image_matcher.handle()
async def _(state: T_State, bot: QQBot):
    _ = bot.self_id
    state[WITHOUT_URL_FLAG] = True


@search_image_matcher.assign("image")
async def _(image: Match[Image]):
    if image.available:
        search_image_matcher.set_path_arg("image", image.result)


@search_image_matcher.got_path("image", prompt="请发送图片")
async def _(state: T_State, image: Image):
    msg: UniMessage | None = None
    api: str = state[SEARCH_IMAGE_API_FLAG]
    with_url = not state.get(WITHOUT_URL_FLAG, False)

    logger.info(f"Search at {api} with image, with_url: {with_url}")

    if api == "saucenao":
        if search_resp := await search_image.search_image_from_saucenao(image.url):
            msg = await search_image.generate_message_from_saucenao_result(
                search_resp, with_url
            )
    elif api == "tracemoe":
        if search_resp := await search_image.search_image_from_tracemoe(image.url):
            msg = await search_image.generate_message_from_tracemoe_result(
                search_resp, with_url
            )

    if msg:
        await search_image_matcher.finish(msg)

    logger.error("Search image failed")
    await search_image_matcher.finish("搜索失败")
