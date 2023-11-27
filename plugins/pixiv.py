from arclet.alconna import Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Alconna, AlconnaQuery, Query, Image

from essentials.libraries import util

__plugin_meta__ = PluginMetadata(
    name="Pixiv助手", description="提供一些有关 Pixiv 的功能", usage="发id看图，没了", config=None
)


_pixiv_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51",
    "Referer": "https://www.pixiv.net/",
}


_command = on_alconna(
    Alconna(
        "pixiv",
        Args["picture_id", str],
    ),
    block=True,
)


@_command.handle()
async def _(picture_id: Query[str] = AlconnaQuery("picture_id")):
    if await util.can_send_segment(Image):
        await _command.finish("这里发不了图哦")
    picture_id = picture_id.result.strip()
    if picture_id.isdigit():
        data = await util.fetch_json_data(f"https://px2.rainchan.win/json/{picture_id}")
        if data:
            if not data["error"]:
                imgurl = data["body"][0]["urls"]["original"]
                # TODO 缓存图片
                imgdata = await util.fetch_bytes_data(imgurl, headers=_pixiv_headers)
                if imgdata:
                    await _command.finish(Image(raw=imgdata))
                else:
                    await _command.finish("图片下载失败")
            else:
                await _command.finish(data["message"])
        else:
            await _command.finish("图片查找失败")
    else:
        await _command.finish("图片id无效")
