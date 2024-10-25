import json
from typing import Annotated
from urllib.parse import urlparse, quote

from nonebot_plugin_alconna import UniMessage

from canrotbot.essentials.libraries.util import can_send_url
from canrotbot.libraries.llm.tool import BaseTool
from canrotbot.libraries.mediawiki import MediaWikiClient
from ..config import llm_plugin_config

HOSTS_URL = {
    "中文维基百科": "https://zh.wikipedia.org/w/api.php",
    # "日文维基百科": "https://jp.wikipedia.org/w/api.php",
    "英文维基百科": "https://en.wikipedia.org/w/api.php",
    "萌娘百科": "https://moegirl.uk/api.php",
    "神奇宝贝百科": "https://wiki.52poke.com/api.php",
}

HOSTS_DESCRIPTION = [
    {
        "name": "中文维基百科",
        "description": "在中文维基百科上可以查到几乎所有中国文化和中文相关内容。如果你不知道选择哪个百科，可以优先选择中文维基百科。当中文维基百科上没有相关内容时，可以尝试日文维基百科。",
    },
    # {
    #     "name": "日文维基百科",
    #     "description": "在日文维基百科上可以查到几乎所有日本文化和日文相关内容。当日文维基百科上没有相关内容时，可以尝试英文维基百科。",
    # },
    {
        "name": "英文维基百科",
        "description": "在英文维基百科上可以查到几乎所有内容，是内容涵盖最全面的百科。当英文维基百科上没有相关内容时，可以尝试其他百科。",
    },
    {
        "name": "萌娘百科",
        "description": "可以查到所有漫画、动漫、游戏等二次元相关的内容，是二次元内容涵盖最全面的百科。如果是动漫、漫画等二次元ACG相关内容，就优先选择萌娘百科。",
    },
    {
        "name": "神奇宝贝百科",
        "description": "可以查到所有神奇宝贝（宝可梦）相关的内容，是神奇宝贝相关内容涵盖最全面的百科",
    },
]


class MediaWikiTool(BaseTool):
    __description__ = (
        f"提供从不同百科搜索词条，并获取最相关词条对应的页面内容的能力。"
        + f"当前支持的百科有："
        + "；".join([i["name"] + "，" + i["description"] for i in HOSTS_DESCRIPTION])
        + "需要根据关键词所属的不同领域选择最合适的百科。"
    )
    __command__ = False

    def __init__(self):
        super().__init__()
        self.client = MediaWikiClient("")
        self.action = ""
        self.target = ""
        self.keyword = ""

    async def __call__(
        self,
        action: Annotated[
            str,
            "hosts为获取所有可用的百科名称及其能搜索到的内容；search为在百科上进行搜索并获取最相关的一个页面标题；get为根据标题获取页面文本。hosts和search的结果不能直接作为回答，需要再通过get获取页面内容，根据页面内容进行回答。get接受的参数为search中返回的title字段。",
        ],
        target: Annotated[
            str,
            "action为hosts时，target被忽略，可以填入空字符串；search和get时为要进行搜索和获取页面内容的百科名称",
        ],
        keyword: Annotated[
            str,
            "进行搜索的关键词或页面标题，根据action的不同，keyword的含义也不同：search时为搜索关键词；get时为页面标题，来自于search的title字段",
        ],
    ) -> str:
        # 保存参数
        self.action = action
        self.target = target
        self.keyword = keyword

        if action == "hosts":
            return json.dumps(HOSTS_DESCRIPTION, ensure_ascii=False)

        if target not in HOSTS_URL:
            return "未知百科名称"
        self.client.base_url = HOSTS_URL[target or "维基百科"]

        if action == "search":
            data = await self.client.search(keyword)
            if not data["query"]["search"]:
                return "未找到相关页面"
            return json.dumps(data, ensure_ascii=False)
        elif action == "get":
            data = await self.client.get_wikitext(keyword)
            content = data["parse"]["wikitext"]

            # Wikipedia API 返回的内容是字典，需要取出其中的内容
            if isinstance(content, dict):
                content = content["*"]

            content = content[0 : llm_plugin_config.max_length]  # 防止内容过长
            return json.dumps(
                {"page_content": content},
                ensure_ascii=False,
            )
        else:
            return "未知操作"

    async def message_postprocess(self, message: UniMessage) -> UniMessage:
        if self.action == "get":
            message += f"\n\n来源：{self.target} - {self.keyword}"
            if can_send_url():
                url = urlparse(self.client.base_url)
                prefix = "wiki/" if self.target.endswith("维基百科") else ""
                message += (
                    f"\n{url.scheme}://{url.netloc}/{prefix}{quote(self.keyword)}"
                )
        return message
