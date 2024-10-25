from typing import Any

from canrotbot.essentials.libraries import network
from . import models


class MediaWikiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_api(self, params: dict[str, str]) -> Any:
        """
        从 MediaWiki API 获取数据

        :param params: 请求参数

        :return: API 返回的数据，固定为 JSON 格式
        """
        params["format"] = "json"
        return await network.fetch_json_data(
            self.base_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        )

    async def search(self, keyword: str) -> models.search.Response:
        """
        搜索 MediaWiki 上的页面

        :param keyword: 搜索关键词

        :return: 搜索结果
        """
        return await self.fetch_api(
            {
                "action": "query",
                "list": "search",
                "srsearch": keyword,
            }
        )

    async def get_wikitext(self, title: str) -> models.parse.Response:
        """
        获取页面的 Wikitext 内容

        :param title: 页面标题

        :return: 页面的 Wikitext 内容
        """
        return await self.fetch_api(
            {
                "action": "parse",
                "page": title,
                "prop": "wikitext",
            }
        )


__all__ = [
    "MediaWikiClient",
]
