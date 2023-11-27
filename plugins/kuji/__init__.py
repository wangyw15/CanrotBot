from arclet.alconna import Alconna
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Image

from essentials.libraries import user, economy
from essentials.libraries import util
from . import kuji

__plugin_meta__ = PluginMetadata(
    name="浅草寺", description="赛博浅草寺", usage="/<kuji|浅草寺>", config=None
)

_command = on_alconna(
    Alconna(
        "kuji",
    ),
    block=True,
)


@_command.handle()
async def _():
    if not economy.pay(await user.get_uid(), 10, "赛博浅草寺求签"):
        await _command.finish("你的余额不足哦")
    await _command.send("谢谢你的十个胡萝卜片喵~")

    if await util.can_send_segment(Image):
        img, _ = await kuji.generate_kuji()
        await _command.finish(Image(raw=img))
    else:
        _, data = await kuji.generate_kuji("")
        await _command.finish(
            f"{data['count']} - {data['type']}\n\n"
            + "\n".join(data["content"])
            + "\n\n"
            + f"{data['straight']}\n\n"
            + "\n".join(data["mean"])
        )
