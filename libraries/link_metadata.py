from .config import get_config
from httpx import AsyncClient
import re

bilibili_vid_pattern = r'(?:https?:\/\/)?(?:(?:www\.)?bilibili.com\/video|b23\.tv)\/((?:BV|av)[0-9A-Za-z]+)'

if proxy := get_config('canrot_proxy'):
    _client = AsyncClient(proxies=proxy)
else:
    _client = AsyncClient()

async def fetch_bilibili_data(vid: str) -> dict | None:
    if vid.startswith('BV'):
        resp = await _client.get(f'https://api.bilibili.com/x/web-interface/view?bvid={vid}')
    elif vid.startswith('av'):
        resp = await _client.get(f'https://api.bilibili.com/x/web-interface/view?aid={vid}')
    if resp and resp.is_success and resp.status_code == 200:
        data = resp.json()
        if data['code'] == 0:
            return data['data']
    return None

async def get_bvid_from_bilibili_short_link(url: str) -> str | None:
    resp = await _client.get(url, allow_redirects=False)
    if resp and resp.is_success and resp.status_code == 302:
        return re.match(bilibili_vid_pattern, resp.headers['Location']).group()[0]
    return None

async def fetch_youtube_data(id: str) -> dict:
    pass
