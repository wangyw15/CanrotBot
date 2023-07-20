from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import Bot, Event, MessageSegment
from nonebot.params import ShellCommandArgv, Arg, Message
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from adapters import unified
from . import search_image

__plugin_meta__ = PluginMetadata(
    name="识图",
    description="通过 SauceNAO.com 或者 trace.moe 识图，目前仅支持QQ直接发送图片搜索",
    usage="先发送/<识图|搜图>，再发图片或者图片链接",
    config=search_image.SearchImageConfig,
)


_search_image = on_shell_command("识图", aliases={"搜图"}, block=True)
@_search_image.handle()
async def _(state: T_State, bot: Bot, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    api = "saucenao"
    if len(args) == 1:
        msg = args[0].lower()
        if msg == "saucenao":
            api = "saucenao"
        elif msg == "tracemoe":
            api = "tracemoe"
        elif msg == "help" or msg == "帮助":
            await _search_image.finish(
                "可选择搜图 API:\ntracemoe (trace.moe) 只能搜番剧\nsaucenao (saucenao.com) 默认"
            )
        else:
            await _search_image.finish("无效的搜图网站选项")
    state["SEARCH_IMAGE_API"] = api

    if unified.Detector.is_qq(bot) or unified.Detector.is_kook(bot):
        await _search_image.send("请发送图片或图片链接")
    else:
        await _search_image.send("请发送图片链接")


@_search_image.got("image")
async def _(state: T_State, bot: Bot, event: Event, image: Message = Arg()):
    # get img url
    img_url: str = ""
    if unified.Detector.is_onebot(bot) and image[0].type == 'image' \
            or unified.Detector.is_mirai2(bot) and image[0].type == unified.adapters.mirai2_module.MessageType.IMAGE:
        img_url = image[0].data['url'].strip()
    elif unified.Detector.is_kook(bot) and image[0].type == 'image':
        img_url = image[0].data['file_key'].strip()
    else:
        img_url = image.extract_plain_text().strip()

    # search
    if img_url and (img_url.startswith("https://") or img_url.startswith("http://")):
        msg = unified.Message()
        api: str = state["SEARCH_IMAGE_API"]
        if api == "saucenao":
            search_resp = await search_image.search_image_from_saucenao(img_url)
            if search_resp:
                msg = search_image.generate_message_from_saucenao_result(search_resp)
            else:
                await _search_image.finish("搜索失败")
        elif api == "tracemoe":
            search_resp = await search_image.search_image_from_tracemoe(img_url)
            if search_resp:
                msg = search_image.generate_message_from_tracemoe_result(search_resp)
            else:
                await _search_image.finish("搜索失败")
        await msg.send()
        await _search_image.finish()
    else:
        await _search_image.finish("图片链接错误，停止搜图")
