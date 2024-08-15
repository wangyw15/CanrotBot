import json
from typing import Annotated

from libraries.llm.tool import BaseTool
from libraries.mediawiki import MediaWikiClient


class MoegirlTool(BaseTool):
    __description__ = "从萌娘百科搜索词条并获取最相关词条对应的页面内容，在萌娘百科上可以查到所有ACG相关的内容"
    __command__ = False

    def __init__(self):
        super().__init__()
        self.client = MediaWikiClient("https://moegirl.uk/api.php")

    async def __call__(
        self,
        action: Annotated[
            str,
            "search为在萌娘百科上进行搜索并获取最相关的一个页面标题；get为根据标题获取页面文本。search的结果不能直接作为回答，需要再通过get获取页面内容，根据页面内容进行回答",
        ],
        keyword: Annotated[str, "进行搜索的关键词或页面标题"],
    ) -> str:
        if action == "search":
            data = await self.client.search(keyword)
            if not data["query"]["search"]:
                return "未找到相关页面"
            return json.dumps(
                {"title": data["query"]["search"][0]["title"]}, ensure_ascii=False
            )
        elif action == "get":
            data = await self.client.get_wikitext(keyword)
            return json.dumps(
                {"page_content": data["parse"]["wikitext"]}, ensure_ascii=False
            )
        else:
            return "未知操作"


class PokeTool(BaseTool):
    __description__ = "从神奇宝贝百科搜索词条并获取最相关词条对应的页面内容，在神奇宝贝百科上可以查到所有神奇宝贝（宝可梦）相关的内容"
    __command__ = False

    def __init__(self):
        super().__init__()
        self.client = MediaWikiClient("https://wiki.52poke.com/api.php")

    async def __call__(
        self,
        action: Annotated[
            str,
            "search为在神奇宝贝百科上进行搜索并获取最相关的一个页面标题；get为根据标题获取页面文本。search的结果不能直接作为回答，需要获取页面内容再进行回答",
        ],
        keyword: Annotated[str, "进行搜索的关键词或页面标题"],
    ) -> str:
        if action == "search":
            data = await self.client.search(keyword)
            if not data["query"]["search"]:
                return "未找到相关页面"
            return json.dumps(
                {"title": data["query"]["search"][0]["title"]}, ensure_ascii=False
            )
        elif action == "get":
            data = await self.client.get_wikitext(keyword)
            return json.dumps(
                {"page_content": data["parse"]["wikitext"]}, ensure_ascii=False
            )
        else:
            return "未知操作"
