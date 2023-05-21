from .config import get_config
from httpx import AsyncClient, Response
import re

bilibili_vid_pattern = r'(?:https?:\/\/)?(?:(?:www\.)?bilibili.com\/video|b23\.tv)\/((?:BV|av)[0-9A-Za-z]+)'
youtube_id_pattern = r'(?:https?:\/\/)?(?:youtu\.be\/|(?:\w{3}\.)?youtube\.com\/watch\?.*v=)([a-zA-Z0-9-_]+)'

if proxy := get_config('canrot_proxy'):
    _client = AsyncClient(proxies=proxy)
else:
    _client = AsyncClient()

async def fetch_bilibili_data(vid: str) -> dict | None:
    resp: Response = {}
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
    resp = await _client.get(url, follow_redirects=False)
    if resp and resp.status_code == 302:
        return re.match(bilibili_vid_pattern, resp.headers['Location']).groups()[0]
    return None

async def fetch_youtube_data(id: str) -> dict:
    if api_key := get_config('youtube_api_key'):
        resp = await _client.get(f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2Cstatistics&id={id}&key={get_config("youtube_api_key")}')
        if resp and resp.is_success and resp.status_code == 200:
            data = resp.json()
            if data['pageInfo']['totalResults'] > 0:
                return data['items'][0]
    return {}
