import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, TypeVar

from httpx import AsyncClient

from storage import config

T = TypeVar('T')

_client = AsyncClient()
_available_languages = ['jp', 'en', 'tw', 'cn', 'kr']  # [日服, 国际服, 台服, 国服, 韩服]
_data_path = Path(config.canrot_config.canrot_data_path) / 'bangdream'
_comic_path = _data_path / 'comic'


# 自动创建文件夹
if not _data_path.exists():
    _data_path.mkdir(parents=True)
if not _comic_path.exists():
    _comic_path.mkdir(parents=True)


async def get_comic_list() -> dict[str]:
    """
    获取漫画列表

    单格漫画编号 001

    四格漫画编号 1001

    :return: 漫画列表
    """
    list_path = _comic_path / 'list.json'
    # 本地缓存
    if list_path.exists():
        with list_path.open(encoding='utf-8') as f:
            local_data = json.load(f)
            # 缓存有效七天
            if datetime.fromisoformat(local_data['last_update']) - datetime.now() < timedelta(days=7):
                return local_data['data']
    # 从服务器获取
    resp = await _client.get('https://bestdori.com/api/comics/all.5.json')
    if resp.is_success and resp.status_code == 200:
        data = resp.json()
        with list_path.open('w', encoding='utf-8') as f:
            json.dump({'last_update': datetime.now().isoformat(), 'data': data}, f, ensure_ascii=False)
        return data
    return {}


def get_content_by_language(arr: list[T], language: str = '') -> Tuple[T, str]:
    """
    获取指定语言的内容

    默认优先级：国服 -> 台服 -> 国际服 -> 日服

    :param arr: 内容
    :param language: 语言

    :return: (内容, 语言)
    """
    if language not in _available_languages or arr[_available_languages.index(language)] is None:
        if arr[_available_languages.index('cn')] is not None:
            language = 'cn'
        elif arr[_available_languages.index('tw')] is not None:
            language = 'tw'
        elif arr[_available_languages.index('en')] is not None:
            language = 'en'
        elif arr[_available_languages.index('jp')] is not None:
            language = 'jp'
    return arr[_available_languages.index(language)], language


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
    title, language = get_content_by_language(comic_list[comic_id]['title'], language)

    if len(comic_id) == 4 and comic_id.startswith('1'):
        return ((f'https://bestdori.com/assets/{language}/comic/comic_fourframe/'
                f'comic_fourframe_{comic_id[1:]}_rip/comic_fourframe_{comic_id[1:]}.png'), language)
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
    title, language = get_content_by_language(comic_list[comic_id]['title'], language)

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
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        comic_path.write_bytes(resp.content)
        return resp.content, language
    return None
