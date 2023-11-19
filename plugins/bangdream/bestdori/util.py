import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, TypeVar

from httpx import AsyncClient

from storage import config

client = AsyncClient()
data_path = Path(config.canrot_config.canrot_data_path) / 'bangdream'
cache_path = data_path / 'cache'
available_languages = ['jp', 'en', 'tw', 'cn', 'kr']  # [日服, 国际服, 台服, 国服, 韩服]
T = TypeVar('T')

_bestdori_cache_path = cache_path / 'bestdori'

# 自动创建文件夹
if not data_path.exists():
    data_path.mkdir(parents=True)


def get_content_by_language(arr: list[T], language: str = '') -> Tuple[T, str]:
    """
    获取指定语言的内容

    默认优先级：国服 -> 台服 -> 国际服 -> 日服

    :param arr: 内容
    :param language: 语言

    :return: (内容, 语言)
    """
    if language not in available_languages or arr[available_languages.index(language)] is None:
        if arr[available_languages.index('cn')] is not None:
            language = 'cn'
        elif arr[available_languages.index('tw')] is not None:
            language = 'tw'
        elif arr[available_languages.index('en')] is not None:
            language = 'en'
        elif arr[available_languages.index('jp')] is not None:
            language = 'jp'
    return arr[available_languages.index(language)], language


async def bestdori_api_with_cache(path: str, valid_duration: timedelta = None) -> dict[str]:
    """
    获取数据并缓存，默认缓存永久有效

    :param path: Bestdori api路径（不带/api）
    :param valid_duration: 缓存有效期

    :return: 数据
    """
    path = path.strip('/')
    cache_file = _bestdori_cache_path / path

    # 本地缓存
    if cache_file.exists():
        with (cache_file.open(encoding='utf-8') as f):
            local_data = json.load(f)
            # 检查缓存是否过期
            if valid_duration is None \
                    or datetime.fromisoformat(local_data['last_update']) - datetime.now() < valid_duration:
                return local_data['data']

    # 自动创建文件夹
    if not cache_file.parent.exists():
        cache_file.parent.mkdir(parents=True)

    # 从服务器获取
    resp = await client.get('https://bestdori.com/api/' + path)
    if resp.is_success and resp.status_code == 200:
        data = resp.json()
        with cache_file.open('w', encoding='utf-8') as f:
            json.dump({'last_update': datetime.now().isoformat(), 'data': data}, f, ensure_ascii=False)
        return data
    return {}
