from typing import Tuple

from bs4 import BeautifulSoup

from ...adapters import unified


async def get_line_sticker(sticker_id: str) -> Tuple[str, bytes]:
    info_resp = await unified.util.fetch_bytes_data(f'https://store.line.me/stickershop/product/{sticker_id}/en')
    info_resp = info_resp.decode('utf-8')
    soup = BeautifulSoup(info_resp, 'html.parser')
    sticker_name = soup.select_one('h2:nth-child(2)').text.strip()
    # 文件
    file_data = await unified.util.fetch_bytes_data(
        f'https://stickershop.line-scdn.net/stickershop/v1/product/{sticker_id}/iphone/stickerpack@2x.zip')
    if not file_data:
        file_data = await unified.util.fetch_bytes_data(
            f'https://stickershop.line-scdn.net/stickershop/v1/product/{sticker_id}/iphone/stickers@2x.zip')
    return sticker_name, file_data
