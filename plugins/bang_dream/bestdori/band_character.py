from datetime import timedelta

from . import util


def get_character_list() -> dict[str]:
    """
    获取角色列表

    :return: 角色列表
    """
    return util.bestdori_api_with_cache("characters/main.3.json", timedelta(days=7))


def get_character_info(character_id: str) -> dict[str]:
    """
    获取角色信息

    :param character_id: 角色ID

    :return: 角色信息
    """
    return util.bestdori_api_with_cache(f"characters/{character_id}.json")


def get_band_list() -> dict[str]:
    """
    获取乐团列表

    :return: 乐团列表
    """
    return util.bestdori_api_with_cache("bands/main.1.json", timedelta(days=7))
