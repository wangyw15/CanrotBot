from typing import Tuple, TypeVar

from canrotbot.essentials.libraries import network

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


async def bestdori_api(path: str) -> dict[str]:
    """
    获取数据并缓存，默认缓存永久有效

    :param path: Bestdori api路径（不带/api）

    :return: 数据
    """
    return await network.fetch_json_data(
        "https://bestdori.com/api/" + path, use_proxy=True
    )
