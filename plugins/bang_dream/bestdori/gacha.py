from . import util


async def get_gacha_list() -> dict[str]:
    """
    获取抽卡列表

    :return: 抽卡列表
    """
    return await util.bestdori_api_with_cache("gacha/all.5.json")


async def get_gacha_info(gacha_id: int) -> dict[str]:
    """
    获取抽卡信息

    :param gacha_id: 抽卡ID

    :return: 抽卡信息
    """
    return await util.bestdori_api_with_cache(f"gacha/{gacha_id}.json")
