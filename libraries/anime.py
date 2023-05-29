import asyncio
import difflib
import json
import urllib.parse
from pathlib import Path
from typing import Tuple

from nonebot import logger
from . import universal_adapters

_anime_offline_database_path = Path(__file__).parent.parent / 'assets/anime-offline-database'
_animes: list[dict] = []


def _load_animes() -> None:
    global _animes
    if not _animes:
        with open(_anime_offline_database_path / 'anime-offline-database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            _animes = data['data']
            logger.info(f'Anime databasee last update time: {data["lastUpdate"]}')
            logger.info(f'Loaded animes: {len(_animes)}')


_load_animes()


def search_anime_by_name(name: str) -> Tuple[str, dict, float]:
    """
    搜索番剧
    :param name: 番剧名
    :return: 番剧名, 番剧信息, 匹配度
    """
    best: float = 0.0
    result = {}
    result_name = ''
    for anime in _animes:
        ratio = difflib.SequenceMatcher(None, name, anime['title']).quick_ratio()
        if ratio > best:
            best = ratio
            result = anime
            result_name = anime['title']
        else:
            for synonym in anime['synonyms']:
                ratio = difflib.SequenceMatcher(None, name, synonym).quick_ratio()
                if ratio > best:
                    best = ratio
                    result = anime
                    result_name = synonym
    return result_name, result, best


def search_anime_by_anilist_id(anilist_id: str | int) -> dict | None:
    url = f'https://anilist.co/anime/{anilist_id}'
    for anime in _animes:
        if url in anime['sources']:
            return anime
    return None


async def search_anime_by_image(img_url: str) -> dict | None:
    """
    通过 trace.moe 以图搜番
    :param img_url: 图片
    :return: 番剧信息
    """
    api_url = "https://api.trace.moe/search?url={url}"
    if data := await universal_adapters.fetch_json_data(api_url.format(url=urllib.parse.quote_plus(img_url))):
        return data
    return None


async def _test() -> None:
    print(search_anime_by_anilist_id(101905))
    while True:
        name = input('Name: ')
        result_name, anime, possibility = search_anime_by_name(name)
        print(result_name)
        print(anime['title'])
        print(possibility)

if __name__ == '__main__':
    asyncio.run(_test())
