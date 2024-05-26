import asyncio
import difflib
import re
import urllib.parse
from typing import Tuple

from nonebot import logger

from essentials.libraries import util
from storage import asset
from datetime import timedelta

# TODO 改为Anilist API
_anime_offline_database = asset.RemoteAsset(
    "https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database-minified.json",
    expire=timedelta(days=7),
)
_animes: list[dict] = []
# _anilist_id_name: dict[int, str] = {}
_name_anilist_id: dict[str, int] = {}


def _load_animes() -> None:
    global _animes, _name_anilist_id
    if not _animes:
        data = _anime_offline_database.json()
        _animes = data["data"]
        logger.info(f'Anime database last update time: {data["lastUpdate"]}')
        logger.info(f"Loaded animes: {len(_animes)}")
    # 提升搜索速度
    logger.info("预加载搜索数据")
    for i in _animes:
        anilist_id = ""
        for url in i["sources"]:
            if result := re.search(r"anilist\.co/anime/(\d+)", url):
                anilist_id = result.groups()[0]
                break
        if not anilist_id:
            continue
        _name_anilist_id[i["title"]] = int(anilist_id)
        for synonym in i["synonyms"]:
            _name_anilist_id[synonym] = int(anilist_id)


_load_animes()


def search_anime_by_name(name: str) -> Tuple[str, dict, float]:
    """
    搜索番剧
    :param name: 番剧名
    :return: 番剧名, 番剧信息, 匹配度
    """
    best: float = 0.0
    result = {}
    result_name = ""
    for anime in _animes:
        ratio = difflib.SequenceMatcher(None, name, anime["title"]).quick_ratio()
        if ratio > best:
            best = ratio
            result = anime
            result_name = anime["title"]
        else:
            for synonym in anime["synonyms"]:
                ratio = difflib.SequenceMatcher(None, name, synonym).quick_ratio()
                if ratio > best:
                    best = ratio
                    result = anime
                    result_name = synonym
    return result_name, result, best


def search_anime_by_anilist_id(anilist_id: str | int) -> dict | None:
    """
    通过 AniList id 搜索番剧

    :param anilist_id: AniList id

    :return: 番剧信息
    """
    url = f"https://anilist.co/anime/{anilist_id}"
    for anime in _animes:
        if url in anime["sources"]:
            return anime
    return None


async def search_anime_by_image(img_url: str) -> dict | None:
    """
    通过 trace.moe 以图搜番
    :param img_url: 图片
    :return: 番剧信息
    """
    api_url = "https://api.trace.moe/search?url={url}"
    if data := await util.fetch_json_data(
        api_url.format(url=urllib.parse.quote_plus(img_url))
    ):
        return data
    return None


def search_anilist_id_by_name(name: str) -> Tuple[str, int, float]:
    """
    根据名称搜索 AniList id

    :params name: 番剧名称

    :return: 番剧名, AniList id, 匹配度
    """
    best: float = 0.0
    result = 0
    result_name = ""
    for k, v in _name_anilist_id.items():
        ratio = difflib.SequenceMatcher(None, name, k).quick_ratio()
        if ratio > best:
            best = ratio
            result = v
            result_name = k
    return result_name, result, best


async def _test() -> None:
    print(search_anime_by_anilist_id(101905))
    while True:
        name = input("Name: ")
        result_name, anime, possibility = search_anime_by_name(name)
        print(result_name)
        print(anime["title"])
        print(possibility)


if __name__ == "__main__":
    asyncio.run(_test())
