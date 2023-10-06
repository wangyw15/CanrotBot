import json
import random
from datetime import datetime

from nonebot import logger

from storage import asset

_hitokoto_assets_path = asset.get_assets_path('hitokoto')
_version: dict = {}
_categories: list[dict] = []
_sentences: dict[str, list[dict]] = {}
_all_category_keys = ''


def _timestamp_to_datetime(timestamp: str) -> datetime:
    return datetime.fromtimestamp(float(timestamp) / 1000)


def _load_hitokoto_assets():
    global _version
    global _categories
    global _sentences
    global _all_category_keys
    # load version.json
    if not _version:
        with open(_hitokoto_assets_path / 'version.json', 'r', encoding='utf-8') as f:
            _version = json.load(f)
            logger.info(f'hitokoto sentences_bundle version: {_version["bundle_version"]}')
    # load categories.json
    if not _categories:
        with open(_hitokoto_assets_path / _version["categories"]["path"], 'r', encoding='utf-8') as f:
            _categories = json.load(f)
            logger.info(f'hitokoto sentences_bundle categories count: {len(_categories)}')
    # load sentences
    if not _sentences:
        for category in _categories:
            _all_category_keys += category["key"]
            with open(_hitokoto_assets_path / category["path"], 'r', encoding='utf-8') as f:
                _sentences[category["key"]] = json.load(f)
                logger.info(
                    f'hitokoto sentences_bundle {category["name"]} sentences count: {len(_sentences[category["key"]])}')


def get_categories() -> list[dict[str, str]]:
    for item in _categories:
        yield {'name': item['name'], 'desc': item['desc'], 'key': item['key']}


def get_key_by_name(name: str) -> str:
    return list(filter(lambda x: x['name'] == name, _categories))[0]['key']


def get_name_by_key(key: str) -> str:
    return list(filter(lambda x: x['key'] == key, _categories))[0]['name']


def random_hitokoto(categories: str = '') -> dict:
    """randomly choose a hitokoto"""
    if not categories:
        categories = _all_category_keys
    sentences = []
    for key in categories:
        if key in _all_category_keys:
            sentences.extend(_sentences[key])
    return random.choice(sentences)


def get_hitokoto_by_uuid(uuid: str) -> dict:
    """get hitokoto by uuid"""
    for category in _categories:
        for sentence in _sentences[category['key']]:
            if sentence['uuid'] == uuid:
                return sentence
    return {}


_load_hitokoto_assets()
