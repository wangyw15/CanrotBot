import urllib.parse

from canrotbot.essentials.libraries import network


async def search_anime_by_image(img_url: str) -> dict | None:
    """
    通过 trace.moe 以图搜番
    :param img_url: 图片
    :return: 番剧信息
    """
    api_url = "https://api.trace.moe/search?url={url}"
    if data := await network.fetch_json_data(
        api_url.format(url=urllib.parse.quote_plus(img_url))
    ):
        return data
    return None
