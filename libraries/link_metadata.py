import re

from httpx import AsyncClient, Response

from .config import get_config

bilibili_vid_pattern = r'(?:https?:\/\/)?(?:(?:www\.)?bilibili.com\/video|b23\.tv)\/((?:BV|av)[0-9A-Za-z]+)'
youtube_id_pattern = r'(?:https?:\/\/)?(?:youtu\.be\/|(?:\w{3}\.)?youtube\.com\/watch\?.*v=)([a-zA-Z0-9-_]+)'

if proxy := get_config('canrot_proxy'):
    _client = AsyncClient(proxies=proxy)
else:
    _client = AsyncClient()


async def fetch_bilibili_data(vid: str) -> dict | None:
    resp: Response | None = None
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


async def fetch_youtube_data(ytb_id: str) -> dict:
    if api_key := get_config('youtube_api_key'):
        resp = await _client.get(
            f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2Cstatistics&id={ytb_id}&key={api_key}')
        if resp and resp.is_success and resp.status_code == 200:
            data = resp.json()
            if data['pageInfo']['totalResults'] > 0:
                if 'likeCount' not in data['items'][0]['statistics']:
                    data['items'][0]['statistics']['likeCount'] = '暂无'
                return data['items'][0]
    return {}


async def fetch_youtube_thumbnail(data: dict) -> bytes | None:
    """Fetch bytes from url"""
    resp = await _client.get(data["snippet"]["thumbnails"]["maxres"]["url"])
    if resp.is_success and resp.status_code == 200:
        return resp.content
    return None


async def fetch_steam_app_info(appid: str, steam_lang: str = 'zh-cn', steam_region='cn') -> dict | None:
    resp = await _client.get(
        f'https://store.steampowered.com/api/appdetails/?appids={appid}&l={steam_lang}&cc={steam_region}',
        headers={'Accept-Language': steam_lang})
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None
