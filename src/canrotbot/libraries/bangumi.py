from typing import Any

from canrotbot.essentials.libraries.network import get_client
from canrotbot.llm.tools import register_tool

BANGUMI_API = "https://api.bgm.tv"
_client = get_client()


async def get_airing_calendar() -> list[dict[str, Any]]:
    response = await _client.get(
        BANGUMI_API + "/calendar",
        headers={
            "User-Agent": "wangyw15/CanrotBot (https://github.com/wangyw15/CanrotBot)",
        },
    )

    if not (response.is_success and response.status_code == 200):
        return []

    return response.json()


@register_tool("bangumi_airing_calendar")
async def get_airing_calendar_simple() -> dict[str, Any]:
    """
    从番组计划（Bangumi）获取当前的每日放送日历

    Returns:
        周一到周日的放送列表
    """
    data: list[dict[str, Any]] = await get_airing_calendar()

    ret: dict[str, Any] = {}
    for i in data:
        ret[i["weekday"]["cn"]] = {
            "items": [
                {
                    "name": j["name"],
                    "name_cn": j["name_cn"],
                    "summary": j["summary"],
                    "url": j["url"],
                }
                for j in i["items"]
            ]
        }

    return ret
