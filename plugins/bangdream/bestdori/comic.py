from datetime import timedelta
from typing import Tuple

from . import util

_comic_path = util.cache_path / 'comic'


# 自动创建文件夹
if not _comic_path.exists():
    _comic_path.mkdir(parents=True)


async def get_comic_list() -> dict[str]:
    """
    获取漫画列表

    单格漫画编号 001

    四格漫画编号 1001

    :return: 漫画列表
    """
    return await util.bestdori_api_with_cache('comics/all.5.json', timedelta(days=7))


async def get_comic_url(comic_id: str, language: str = '') -> Tuple[str, str] | None:
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
    title, language = util.get_content_by_language(comic_list[comic_id]['title'], language)

    if len(comic_id) == 4 and comic_id.startswith('1'):
        return ((f'https://bestdori.com/assets/{language}/comic/comic_fourframe/'
                f'comic_fourframe_{comic_id[1:]}_rip/comic_fourframe_{comic_id[1:]}.png'), language)
    comic_id = comic_id.zfill(3)
    return ((f'https://bestdori.com/assets/{language}/comic/comic_singleframe/'
            f'comic_{comic_id}_rip/comic_{comic_id}.png'), language)


async def get_comic(comic_id: str, language: str = '') -> Tuple[bytes, str] | None:
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

    # 按优先级选择语言
    title, language = util.get_content_by_language(comic_list[comic_id]['title'], language)

    # 自动创建文件夹
    language_path = _comic_path / language
    if not language_path.exists():
        language_path.mkdir(parents=True)

    # 查找本地缓存
    comic_path = language_path / f'{comic_id}.png'
    if comic_path.exists():
        return comic_path.read_bytes(), language

    # 从服务器获取
    url, _ = await get_comic_url(comic_id)
    resp = await util.client.get(url)
    if resp.is_success and resp.status_code == 200:
        comic_path.write_bytes(resp.content)
        return resp.content, language
    return None
