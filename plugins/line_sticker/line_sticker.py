from tempfile import NamedTemporaryFile
from typing import Tuple

import nonebot.adapters.kaiheila as kook
import nonebot.adapters.onebot.v11 as ob11
import nonebot.adapters.onebot.v12 as ob12
from bs4 import BeautifulSoup
from nonebot.adapters import Bot, Event

from essentials.libraries import util


async def get_line_sticker(sticker_id: str) -> Tuple[str, bytes]:
    info_resp = await util.fetch_text_data(
        f"https://store.line.me/stickershop/product/{sticker_id}/en"
    )
    soup = BeautifulSoup(info_resp, "html.parser")
    sticker_name = soup.select_one("h2:nth-child(2)").text.strip()
    # 文件
    file_data = await util.fetch_bytes_data(
        f"https://stickershop.line-scdn.net/stickershop/v1/product/{sticker_id}/iphone/stickerpack@2x.zip"
    )
    if not file_data:
        file_data = await util.fetch_bytes_data(
            f"https://stickershop.line-scdn.net/stickershop/v1/product/{sticker_id}/iphone/stickers@2x.zip"
        )
    return sticker_name, file_data


async def send_file(content: bytes, name: str, bot: Bot, event: Event):
    if isinstance(bot, ob11.Bot):
        with NamedTemporaryFile() as f:
            f.write(content)
            f.flush()
            if isinstance(event, ob11.PrivateMessageEvent) or isinstance(
                event, ob12.PrivateMessageEvent
            ):
                await bot.call_api(
                    "upload_private_file",
                    user_id=event.get_user_id(),
                    file=f.name,
                    name=name,
                )
            elif isinstance(event, ob11.GroupMessageEvent) or isinstance(
                event, ob12.GroupMessageEvent
            ):
                await bot.call_api(
                    "upload_group_file", group_id=event.group_id, file=f.name, name=name
                )
    elif isinstance(bot, kook.Bot):
        url = await bot.upload_file(content)
        await bot.send(event, kook.MessageSegment.file(url, name))
    else:
        await bot.send(event, f"[此处暂不支持发送文件，文件名: {name}]")
