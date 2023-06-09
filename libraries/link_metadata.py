from httpx import AsyncClient

from .config import get_config

youtube_id_pattern = r'(?:https?:\/\/)?(?:youtu\.be\/|(?:\w{3}\.)?youtube\.com\/watch\?.*v=)([a-zA-Z0-9-_]+)'

if proxy := get_config('canrot_proxy'):
    _client = AsyncClient(proxies=proxy)
else:
    _client = AsyncClient()


async def fetch_youtube_data(ytb_id: str) -> dict:
    if api_key := get_config('youtube_api_key'):
        resp = await _client.get(
            f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2Cstatistics&id={ytb_id}&key={api_key}')
        if resp and resp.is_success and resp.status_code == 200:
            data = resp.json()
            if data['pageInfo']['totalResults'] > 0:
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
