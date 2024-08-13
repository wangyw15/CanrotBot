from typing import Tuple

from bs4 import BeautifulSoup
from nonebot import logger

from essentials.libraries import network


async def get_line_sticker(sticker_id: str) -> Tuple[str, bytes]:
    info_resp = await network.fetch_text_data(
        f"https://store.line.me/stickershop/product/{sticker_id}/en"
    )
    soup = BeautifulSoup(info_resp, "html.parser")

    # 贴纸信息
    sticker_name = soup.select_one('p[data-test="sticker-name-title"]').text.strip()

    # 下载文件
    file_data = await network.fetch_bytes_data(
        f"https://stickershop.line-scdn.net/stickershop/v1/product/{sticker_id}/iphone/stickerpack@2x.zip"
    )
    if file_data:
        logger.info(f"Downloaded {sticker_name} stickerpack@2x.zip")
    else:
        file_data = await network.fetch_bytes_data(
            f"https://stickershop.line-scdn.net/stickershop/v1/product/{sticker_id}/iphone/stickers@2x.zip"
        )
        logger.info(f"Downloaded {sticker_name} stickers@2x.zip")

    return sticker_name, file_data
