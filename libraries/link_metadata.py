from .config import get_config
from httpx import AsyncClient
import re

if proxy := get_config('canrot_proxy'):
    _client = AsyncClient(proxies=proxy)
else:
    _client = AsyncClient()

async def fetch_bilibili_data(bvid: str, type: str = 'bv') -> dict | None:
    if type == 'bv':
        resp = await _client.get(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')
    elif type == 'av':
        resp = await _client.get(f'https://api.bilibili.com/x/web-interface/view?aid={bvid}')
    if resp and resp.is_success and resp.status_code == 200:
        data = resp.json()
        if data['code'] == 0:
            return data['data']
    return None

async def fetch_youtube_data(id: str) -> dict:
    pass
