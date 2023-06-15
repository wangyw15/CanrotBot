from httpx import AsyncClient
from typing import Tuple
from ..adapters import unified
from bs4 import BeautifulSoup

_client = AsyncClient()


async def get_line_sticker(sticker_id: str) -> Tuple[str, bytes]:
    info_resp = await unified.util.fetch_bytes_data(f'https://store.line.me/stickershop/product/{sticker_id}/en')
    info_resp = info_resp.decode('utf-8')
    soup = BeautifulSoup(info_resp, 'html.parser')
    sticker_name = soup.select_one('.mdCMN38Item01Ttl').text
    # 文件
    file_data = await unified.util.fetch_bytes_data(
        f'https://stickershop.line-scdn.net/stickershop/v1/product/{sticker_id}/iphone/stickerpack@2x.zip')
    if not file_data:
        file_data = await _client.get(
            f'https://stickershop.line-scdn.net/stickershop/v1/product/{sticker_id}/iphone/stickers@2x.zip')
    return sticker_name, file_data
