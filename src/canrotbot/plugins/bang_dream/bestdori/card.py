from . import util


async def get_card_list() -> dict[str]:
    """
    获取卡片列表

    :return: 卡片列表
    """
    return await util.bestdori_api("cards/all.5.json")


async def get_card_info(card_id: str) -> dict[str]:
    """
    获取卡片信息

    :param card_id: 卡片ID

    :return: 卡片信息
    """
    return await util.bestdori_api(f"cards/{card_id}.json")
