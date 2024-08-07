import difflib
import json
import random
from datetime import datetime
from typing import Literal, Tuple

from nonebot import get_driver

from essentials.libraries import network, path, render_by_browser

event_type = [
    "Showtime",
    "Millicolle!",
    "Theater",
    "Tour",
    "Anniversary",
    "Working",
    "April Fool",
    "Game Corner",
    "Millicolle! (Box Gasha)",
    "Twin Stage (High Score by Song)",
    "Tune",
    "Twin Stage (Total High Score)",
    "Tale / Time",
    "Talk Party",
    "Treasure",
]

appeal_type = ["None", "Vocal", "Dance", "Visual"]

ASSET_PATH = path.get_asset_path("mltd")
_cards: list[dict] = []
_cards_zh: list[dict] = []
_cards_for_gasha: dict[int, list[dict]] = {}


@get_driver().on_startup
async def load_cards(force_reload: bool = False) -> None:
    global _cards, _cards_zh, _cards_for_gasha
    if force_reload or not _cards or not _cards_zh:
        _cards = await network.fetch_json_data(
            "https://api.matsurihi.me/api/mltd/v2/cards"
            "?includeCostumes=true&includeParameters=true&includeLines=true&includeSkills=true&includeEvents=true",
            use_cache=True,
            use_proxy=True,
        )
        _cards_zh = await network.fetch_json_data(
            "https://api.matsurihi.me/api/mltd/v2/zh/cards"
            "?includeCostumes=true&includeParameters=true&includeLines=true&includeSkills=true&includeEvents=true",
            use_cache=True,
            use_proxy=True,
        )
        _cards_last_fetch = datetime.now()

        # 生成卡池
        _cards_for_gasha = {}
        for card in _cards:
            if card["rarity"] == 1 or card["exType"] != 0:
                continue
            if card["rarity"] not in _cards_for_gasha:
                _cards_for_gasha[card["rarity"]] = []
            _cards_for_gasha[card["rarity"]].append(card)


def get_cards() -> list[dict]:
    return _cards


def search_card(keyword: str, force_jp: bool = False) -> dict:
    best = 0.0
    ret = {}
    # 优先搜索中文内容
    if not force_jp:
        for card in _cards_zh:
            ratio = difflib.SequenceMatcher(None, keyword, card["name"]).quick_ratio()
            if ratio > best:
                best = ratio
                ret = card
        if keyword in ret["name"]:
            return ret
    # 搜索日文内容
    for card in _cards:
        ratio = difflib.SequenceMatcher(None, keyword, card["name"]).quick_ratio()
        if ratio > best:
            best = ratio
            ret = card
    return ret


async def generate_card_info_image(card: dict) -> bytes:
    html = (
        (ASSET_PATH / "card_info.html")
        .read_text(encoding="utf-8")
        .replace("'{DATA_HERE}'", json.dumps(card))
    )
    return await render_by_browser.render_html(
        html, ASSET_PATH, viewport={"width": 1280, "height": 1000}
    )


async def get_events(time: Literal["now"] | datetime = "now") -> list[dict] | None:
    if time == "now":
        return await network.fetch_json_data(
            f"https://api.matsurihi.me/api/mltd/v2/events?at=now", use_proxy=True
        )
    elif isinstance(time, datetime):
        t = datetime.now().astimezone().replace(microsecond=0).isoformat()
        return await network.fetch_json_data(
            f"https://api.matsurihi.me/api/mltd/v2/events?at={t}", use_proxy=True
        )


async def gasha() -> Tuple[bytes, list[dict]]:
    cards: list[dict] = []
    # SR保底
    got_sr_or_better = False
    # 抽卡
    while len(cards) != 10:
        magic_number = random.random()
        if magic_number < 0.03:
            cards.append(random.choice(_cards_for_gasha[4]))
            got_sr_or_better = True
        elif magic_number < 0.15:
            cards.append(random.choice(_cards_for_gasha[3]))
            got_sr_or_better = True
        else:
            cards.append(random.choice(_cards_for_gasha[2]))
    # SR保底
    if not got_sr_or_better:
        cards[random.randint(0, 9)] = random.choice(_cards_for_gasha[3])
    # 生成图片
    html = (
        (ASSET_PATH / "gasha.html")
        .read_text(encoding="utf-8")
        .replace("'{DATA_HERE}'", json.dumps(cards))
    )
    img = await render_by_browser.render_html(
        html, ASSET_PATH, viewport={"width": 1920, "height": 1080}
    )
    return img, cards
