from typing import Tuple

from canrotbot.essentials.libraries import network
from . import util


async def get_comic_list() -> dict[str]:
    """
    获取漫画列表

    单格漫画编号 001

    四格漫画编号 1001

    :return: 漫画列表
    """
    return await util.bestdori_api("comics/all.5.json")


async def get_comic_url(comic_id: str, language: str = "") -> Tuple[str, str] | None:
    """
    获取漫画链接

    默认优先级：国服 -> 台服 -> 国际服 -> 日服

    :param language: 语言
    :param comic_id: 漫画ID

    :return: (漫画链接, 语言)
    """
    comic_list = await get_comic_list()

    # 确保漫画id存在
    if comic_id not in comic_list:
        return None

    # 按优先级选择语言
    title, language = util.get_content_by_language(
        comic_list[comic_id]["title"], language
    )

    if len(comic_id) == 4 and comic_id.startswith("1"):
        return (
            (
                f"https://bestdori.com/assets/{language}/comic/comic_fourframe/"
                f"comic_fourframe_{comic_id[1:]}_rip/comic_fourframe_{comic_id[1:]}.png"
            ),
            language,
        )
    comic_id = comic_id.zfill(3)
    return (
        (
            f"https://bestdori.com/assets/{language}/comic/comic_singleframe/"
            f"comic_{comic_id}_rip/comic_{comic_id}.png"
        ),
        language,
    )


async def get_comic(comic_id: str, language: str = "") -> Tuple[bytes, str] | None:
    """
    获取漫画

    默认优先级：国服 -> 台服 -> 国际服 -> 日服

    :param comic_id: 漫画ID
    :param language: 语言

    :return: (图片, 语言)
    """
    comic_list = await get_comic_list()

    # 确保漫画id存在
    if comic_id not in comic_list:
        return None

    url, language = get_comic_url(comic_id, language)
    return await network.fetch_bytes_data(url, use_proxy=True), language
