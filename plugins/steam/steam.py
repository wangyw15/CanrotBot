from essentials.libraries.network import fetch_json_data


async def fetch_app_info(
    appid: str, steam_lang: str = "zh-cn", steam_region="cn"
) -> dict | None:
    return await fetch_json_data(
        f"https://store.steampowered.com/api/appdetails/?appids={appid}&l={steam_lang}&cc={steam_region}",
        headers={"Accept-Language": steam_lang},
    )
