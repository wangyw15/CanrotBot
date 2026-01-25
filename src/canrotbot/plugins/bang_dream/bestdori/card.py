from canrotbot.llm.tools import register_tool
from . import util


@register_tool("bang_dream_get_cards_list")
async def get_card_list() -> dict[str]:
    """
    获取Bang Dream游戏中的卡片列表

    Returns:
        带有简略信息的卡片列表
    """
    return await util.bestdori_api("cards/all.5.json")


async def get_card_info(card_id: str) -> dict[str]:
    """
    获取Bang Dream游戏中指定卡片的详细信息

    Args:
        card_id: 卡片ID

    Returns:
        卡片信息
    """
    return await util.bestdori_api(f"cards/{card_id}.json")
