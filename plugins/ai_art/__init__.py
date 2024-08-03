from arclet.alconna import Alconna, Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import Image, on_alconna, Query

from essentials.libraries import user, economy, util
from . import tencent_cloud

__plugin_meta__ = PluginMetadata(
    name="AI 作画",
    description="AI 作画插件，目前支持腾讯云",
    usage="/ai <正向提示词> [反向提示词] [风格]",
    config=None,
)

_ai_art_handler = on_alconna(
    Alconna(
        "ai_art",
        Args["prompt", str]["negative", str, ""]["styles", str, "201"],
    ),
    aliases={"AI", "AI作画", "AI绘画"},
    block=True,
)


@_ai_art_handler.handle()
async def _(
    prompt: Query[str] = Query("prompt"),
    negative: Query[str] = Query("negative", ""),
    styles: Query[str] = Query("styles", "201"),
):
    if not await util.can_send_segment(Image):
        await _ai_art_handler.finish("这里没法图片喵")

    uid = user.get_uid()
    if not uid:
        await _ai_art_handler.finish("未注册用户无法使用 AI 作画")
        return
    if not economy.pay(uid, 100, "AI 作画"):
        await _ai_art_handler.finish("余额不足")
        return
    await _ai_art_handler.send("谢谢你的100个胡萝卜片喵~正在努力画画呢~")

    # 生成请求
    image = tencent_cloud.draw(prompt.result, negative.result, styles.result)
    await _ai_art_handler.finish(Image(raw=image))
