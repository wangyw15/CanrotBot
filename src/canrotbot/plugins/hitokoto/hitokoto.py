import random
from datetime import datetime

from nonebot import logger, get_driver

from canrotbot.essentials.libraries import network
from canrotbot.llm.tools import register_tool

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
async def _on_startup() -> None:
    try:
        await load_hitokoto_assets()
    except Exception as e:
        logger.error("Failed to load hitokoto assets")
        logger.exception(e)


async def load_hitokoto_assets() -> None:
    global version
    global categories
    global sentences
    global all_category_keys

    # 加载 version.json
    if not version:
        version = await network.fetch_json_data(
            RESOURCE_URL.format("version.json"), use_proxy=True
        )
        logger.info(f'hitokoto sentences_bundle version: {version["bundle_version"]}')

    # 加载 categories.json
    if not categories:
        categories = await network.fetch_json_data(
            RESOURCE_URL.format("categories.json"), use_proxy=True
        )
        logger.info(f"hitokoto sentences_bundle categories count: {len(categories)}")

    # 加载 sentences
    if not sentences:
        for category in categories:
            all_category_keys += category["key"]
            sentences[category["key"]] = await network.fetch_json_data(
                RESOURCE_URL.format(category["path"][2:]),
                use_proxy=True,
            )
            logger.info(
                f'hitokoto sentences_bundle {category["name"]} sentences count: {len(sentences[category["key"]])}'
            )


def get_categories() -> list[dict[str, str]] | None:
    if not categories:
        return None

    for item in categories:
        yield {"name": item["name"], "desc": item["desc"], "key": item["key"]}


def get_key_by_name(name: str) -> str | None:
    if not categories:
        return None

    return list(filter(lambda x: x["name"] == name, categories))[0]["key"]


def get_name_by_key(key: str) -> str | None:
    if not categories:
        return None

    return list(filter(lambda x: x["key"] == key, categories))[0]["name"]


@register_tool()
def random_hitokoto(selected_categories: str = all_category_keys) -> dict | None:
    """
    随机生成一条一言内容

    Args:
        selected_categories: a: 动画, b: 漫画, c: 游戏, d: 文学, e: 原创, f: 来自网络, g: 其他, h: 影视, i: 诗词, j: 网易云, k: 哲学, l: 抖机灵, 其他: 作为动画类型处理; 默认为所有种类

    Returns:
        一言信息
    """
    if not sentences or not all_category_keys:
        return None

    selected_sentences = []
    for key in selected_categories:
        if key in all_category_keys:
            selected_sentences.extend(sentences[key])
    return random.choice(selected_sentences)


@register_tool()
def get_hitokoto_by_uuid(uuid: str) -> dict | None:
    """
    根据给定uuid获取对应的一言信息

    Args:
        uuid: 一言的uuid

    Returns:
        一言信息
    """
    if not categories or not sentences:
        return None

    for category in categories:
        for sentence in sentences[category["key"]]:
            if sentence["uuid"] == uuid:
                return sentence
    return {}
