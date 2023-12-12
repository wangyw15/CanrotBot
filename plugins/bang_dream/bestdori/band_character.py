from datetime import timedelta

from . import util


async def get_character_list() -> dict[str]:
    """
    获取角色列表

    :return: 角色列表
    """
    return await util.bestdori_api_with_cache(
        "characters/main.3.json", timedelta(days=7)
    )


async def get_character_info(character_id: str) -> dict[str]:
    """
    获取角色信息

    :param character_id: 角色ID

    :return: 角色信息
    """
    return await util.bestdori_api_with_cache(f"characters/{character_id}.json")


async def get_band_list() -> dict[str]:
    """
    获取乐团列表

    :return: 乐团列表
    """
    return await util.bestdori_api_with_cache("bands/main.1.json", timedelta(days=7))
