import asyncio
import difflib
import json
from pathlib import Path
from typing import Tuple

from nonebot import logger

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


def search_anime(name: str) -> Tuple[str, dict, float]:
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


async def _test() -> None:
    status = set()
    for i in _animes:
        if i['status'] not in status:
            status.add(i['status'])
    print(status)
    while True:
        name = input('Name: ')
        result_name, anime, possibility = search_anime(name)
        print(result_name)
        print(anime['title'])
        print(possibility)

if __name__ == '__main__':
    asyncio.run(_test())
