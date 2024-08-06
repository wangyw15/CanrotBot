import random
from datetime import datetime

from nonebot import logger, get_driver

from essentials.libraries import network

RESOURCE_URL = (
    "https://raw.githubusercontent.com/hitokoto-osc/sentences-bundle/master/{}"
)
version: dict = {}
categories: list[dict] = []
sentences: dict[str, list[dict]] = {}
all_category_keys = ""


def _timestamp_to_datetime(timestamp: str) -> datetime:
    return datetime.fromtimestamp(float(timestamp) / 1000)


@get_driver().on_startup
async def _load_hitokoto_assets():
    global version
    global categories
    global sentences
    global all_category_keys

    # 加载 version.json
    if not version:
        version = await network.fetch_json_data(
            RESOURCE_URL.format("version.json"), use_cache=True, use_proxy=True
        )
        logger.info(f'hitokoto sentences_bundle version: {version["bundle_version"]}')

    # 加载 categories.json
    if not categories:
        categories = await network.fetch_json_data(
            RESOURCE_URL.format("categories.json"), use_cache=True, use_proxy=True
        )
        logger.info(f"hitokoto sentences_bundle categories count: {len(categories)}")

    # 加载 sentences
    if not sentences:
        for category in categories:
            all_category_keys += category["key"]
            sentences[category["key"]] = await network.fetch_json_data(
                RESOURCE_URL.format(category["path"][2:]),
                use_cache=True,
                use_proxy=True,
            )
            logger.info(
                f'hitokoto sentences_bundle {category["name"]} sentences count: {len(sentences[category["key"]])}'
            )


def get_categories() -> list[dict[str, str]]:
    for item in categories:
        yield {"name": item["name"], "desc": item["desc"], "key": item["key"]}


def get_key_by_name(name: str) -> str:
    return list(filter(lambda x: x["name"] == name, categories))[0]["key"]


def get_name_by_key(key: str) -> str:
    return list(filter(lambda x: x["key"] == key, categories))[0]["name"]


def random_hitokoto(selected_categories: str = all_category_keys) -> dict:
    """
    随机一言

    :param selected_categories: 选择的分类，不填则随机选择

    :return: 一言信息
    """
    selected_sentences = []
    for key in selected_categories:
        if key in all_category_keys:
            selected_sentences.extend(sentences[key])
    return random.choice(selected_sentences)


def get_hitokoto_by_uuid(uuid: str) -> dict:
    """
    根据uuid获取一言信息

    :param uuid: 一言的uuid

    :return: 一言信息
    """
    for category in categories:
        for sentence in sentences[category["key"]]:
            if sentence["uuid"] == uuid:
                return sentence
    return {}
