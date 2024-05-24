from httpx import AsyncClient

from storage import config


if proxy := config.get_config("canrot_proxy"):
    _client = AsyncClient(proxy=proxy)
else:
    _client = AsyncClient()


async def fetch_app_info(
    appid: str, steam_lang: str = "zh-cn", steam_region="cn"
) -> dict | None:
    resp = await _client.get(
        f"https://store.steampowered.com/api/appdetails/?appids={appid}&l={steam_lang}&cc={steam_region}",
        headers={"Accept-Language": steam_lang},
    )
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None
