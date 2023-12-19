import asyncio
import random
from datetime import datetime, timedelta

from nonebot import logger

from storage import asset

_hitokoto_asset = asset.GithubAssetManager(
    "hitokoto-osc/sentences-bundle", expire=timedelta(days=31)
)
_version: dict = {}
_categories: list[dict] = []
_sentences: dict[str, list[dict]] = {}
_all_category_keys = ""


def _timestamp_to_datetime(timestamp: str) -> datetime:
    return datetime.fromtimestamp(float(timestamp) / 1000)


# TODO 自动更新资源
async def _load_hitokoto_assets():
    global _version
    global _categories
    global _sentences
    global _all_category_keys

    # 加载 version.json
    if not _version:
        _version = await _hitokoto_asset("version.json").json()
        logger.info(f'hitokoto sentences_bundle version: {_version["bundle_version"]}')

    # 加载 categories.json
    if not _categories:
        _categories = await _hitokoto_asset("categories.json").json()
        logger.info(f"hitokoto sentences_bundle categories count: {len(_categories)}")

    # 加载 sentences
    if not _sentences:
        for category in _categories:
            _all_category_keys += category["key"]
            _sentences[category["key"]] = await _hitokoto_asset(
                category["path"][2:]
            ).json()
            logger.info(
                f'hitokoto sentences_bundle {category["name"]} sentences count: {len(_sentences[category["key"]])}'
            )


with asyncio.Runner() as runner:
    runner.run(_load_hitokoto_assets())


def get_categories() -> list[dict[str, str]]:
    for item in _categories:
        yield {"name": item["name"], "desc": item["desc"], "key": item["key"]}


def get_key_by_name(name: str) -> str:
    return list(filter(lambda x: x["name"] == name, _categories))[0]["key"]


def get_name_by_key(key: str) -> str:
    return list(filter(lambda x: x["key"] == key, _categories))[0]["name"]


def random_hitokoto(categories: str = "") -> dict:
    """
    随机一言

    :param categories: 选择的分类，不填则随机选择

    :return: 一言信息
    """
    if not categories:
        categories = _all_category_keys
    sentences = []
    for key in categories:
        if key in _all_category_keys:
            sentences.extend(_sentences[key])
    return random.choice(sentences)


def get_hitokoto_by_uuid(uuid: str) -> dict:
    """
    根据uuid获取一言信息

    :param uuid: 一言的uuid

    :return: 一言信息
    """
    for category in _categories:
        for sentence in _sentences[category["key"]]:
            if sentence["uuid"] == uuid:
                return sentence
    return {}
