from arclet.alconna import Alconna, Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import Image, on_alconna, Query, CommandMeta

from canrotbot.essentials.libraries import user, economy, util
from . import tencent_cloud

ai_art_command = Alconna(
    "ai_art",
    Args["prompt", str]["negative", str, ""]["styles", str, "201"],
    meta=CommandMeta(description="AI 作画插件，目前支持腾讯云"),
)

__plugin_meta__ = PluginMetadata(
    name="AI 作画",
    description=ai_art_command.meta.description,
    usage=ai_art_command.get_help(),
    config=None,
)

ai_art_matcher = on_alconna(
    Alconna(
        "ai_art",
        Args["prompt", str]["negative", str, ""]["styles", str, "201"],
    ),
    aliases={"AI", "AI作画", "AI绘画"},
    block=True,
)


@ai_art_matcher.handle()
async def _(
    prompt: Query[str] = Query("prompt"),
    negative: Query[str] = Query("negative", ""),
    styles: Query[str] = Query("styles", "201"),
):
    if not await util.can_send_segment(Image):
        await ai_art_matcher.finish("这里没法图片喵")

    uid = user.get_uid()
    if not uid:
        await ai_art_matcher.finish("未注册用户无法使用 AI 作画")
        return
    if not economy.pay(uid, 100, "AI 作画"):
        await ai_art_matcher.finish("余额不足")
        return
    await ai_art_matcher.send("谢谢你的100个胡萝卜片喵~正在努力画画呢~")

    # 生成请求
    image = tencent_cloud.draw(prompt.result, negative.result, styles.result)
    await ai_art_matcher.finish(Image(raw=image))


@ai_art_matcher.handle()
async def _default():
    await ai_art_matcher.finish(ai_art_command.get_help())
