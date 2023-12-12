from datetime import timedelta
from pathlib import Path
from typing import Tuple, TypeVar

from httpx import AsyncClient

from storage import asset, config

client = AsyncClient()
available_languages = ["jp", "en", "tw", "cn", "kr"]  # [日服, 国际服, 台服, 国服, 韩服]
T = TypeVar("T")


def get_content_by_language(arr: list[T], language: str = "") -> Tuple[T, str]:
    """
    获取指定语言的内容

    默认优先级：国服 -> 台服 -> 国际服 -> 日服

    :param arr: 内容
    :param language: 语言

    :return: (内容, 语言)
    """
    if (
        language not in available_languages
        or arr[available_languages.index(language)] is None
    ):
        if arr[available_languages.index("cn")] is not None:
            language = "cn"
        elif arr[available_languages.index("tw")] is not None:
            language = "tw"
        elif arr[available_languages.index("en")] is not None:
            language = "en"
        elif arr[available_languages.index("jp")] is not None:
            language = "jp"
    return arr[available_languages.index(language)], language


async def bestdori_api_with_cache(
    path: str, valid_duration: timedelta = None
) -> dict[str]:
    """
    获取数据并缓存，默认缓存永久有效

    :param path: Bestdori api路径（不带/api）
    :param valid_duration: 缓存有效期

    :return: 数据
    """
    url = "https://bestdori.com/api/" + path
    file = asset.RemoteAsset(url, expire=valid_duration)
    return await file.json()
