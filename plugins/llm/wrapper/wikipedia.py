import json
from typing import Annotated

from libraries.llm.tool import BaseTool
from libraries.mediawiki import MediaWikiClient


class WikipediaTool(BaseTool):
    __description__ = "从维基百科搜索词条并获取最相关词条对应的页面内容，在维基百科上可以查到几乎所有内容"
    __command__ = False

    def __init__(self):
        super().__init__()
        self.client = MediaWikiClient("https://en.wikipedia.org/w/api.php")

    async def __call__(
        self,
        action: Annotated[
            str,
            "search为在维基百科上进行搜索并获取最相关的一个页面标题；get为根据标题获取页面文本。search的结果不能直接作为回答，需要再通过get获取页面内容，根据页面内容进行回答。get接受的参数为search中返回的title字段",
        ],
        keyword: Annotated[
            str,
            "进行搜索的关键词或页面标题，根据action的不同，keyword的含义也不同：search时为搜索关键词；get时为页面标题，来自于search的title字段",
        ],
    ) -> str:
        if action == "search":
            data = await self.client.search(keyword)
            if not data["query"]["search"]:
                return "未找到相关页面"
            return json.dumps(data)
        elif action == "get":
            data = await self.client.get_wikitext(keyword)
            return json.dumps(
                {"page_content": data["parse"]["wikitext"]}, ensure_ascii=False
            )
        else:
            return "未知操作"
