from httpx import AsyncClient

from storage import config

youtube_id_pattern = r"(?:https?:\/\/)?(?:youtu\.be\/|(?:\w{3}\.)?youtube\.com\/watch\?.*v=)([a-zA-Z0-9-_]+)"

if proxy := config.get_config("canrot_proxy"):
    _client = AsyncClient(proxies=proxy)
else:
    _client = AsyncClient()


async def fetch_youtube_data(ytb_id: str) -> dict:
    if api_key := config.get_config("youtube_api_key"):
        resp = await _client.get(
            f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2Cstatistics&id={ytb_id}&key={api_key}"
        )
        if resp and resp.is_success and resp.status_code == 200:
            data = resp.json()
            if data["pageInfo"]["totalResults"] > 0:
                return data["items"][0]
    return {}


async def fetch_youtube_thumbnail(data: dict) -> bytes | None:
    """
    下载 YouTube 封面图

    :param data: YouTube 接口返回的数据

    :return: 封面图数据
    """
    url = ""
    max_width = 0
    for _, v in data["snippet"]["thumbnails"].items():
        if v["width"] > max_width:
            max_width = v["width"]
            url = v["url"]
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        return resp.content
    return None
