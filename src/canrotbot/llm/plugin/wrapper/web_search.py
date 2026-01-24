import json

from canrotbot.libraries.llm.tool import BaseTool


class WebSearch(BaseTool):
    __tool_type__ = "builtin_function"
    __tool_name__ = "$web_search"

    async def __call__(self, **kwargs) -> str:
        return json.dumps(kwargs)
