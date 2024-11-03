import difflib
from datetime import datetime
from typing import Literal

from nonebot import get_driver, logger

from canrotbot.essentials.libraries import network

EVENT_TYPE = [
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
APPEAL_TYPE = ["None", "Vocal", "Dance", "Visual"]

cards: list[dict] = []
cards_for_gasha: dict[int, list[dict]] = {}


@get_driver().on_startup
async def _on_startup() -> None:
    try:
        await load_cards()
    except Exception as e:
        logger.error("Failed to load cards")
        logger.exception(e)


async def load_cards(force_reload: bool = False) -> None:
    global cards, cards_for_gasha
    if force_reload or not cards:
        cards = await network.fetch_json_data(
            "https://api.matsurihi.me/api/mltd/v2/cards" +
            "?includeCostumes=true&includeParameters=true&includeLines=true&includeSkills=true&includeEvents=true",
            use_cache=True,
            use_proxy=True,
        )
        _cards_last_fetch = datetime.now()

        # 生成卡池
        cards_for_gasha = {}
        for card in cards:
            if card["rarity"] == 1 or card["exType"] != 0:
                continue
            if card["rarity"] not in cards_for_gasha:
                cards_for_gasha[card["rarity"]] = []
            cards_for_gasha[card["rarity"]].append(card)


def get_cards() -> list[dict] | None:
    if not cards:
        return None

    return cards


def search_card(keyword: str) -> dict | None:
    if not cards:
        return None

    best = 0.0
    ret = {}

    for card in cards:
        ratio = difflib.SequenceMatcher(None, keyword, card["name"]).quick_ratio()
        if ratio > best:
            best = ratio
            ret = card
    return ret


async def get_events(time: Literal["now"] | datetime = "now") -> list[dict] | None:
    if time == "now":
        return await network.fetch_json_data(
            "https://api.matsurihi.me/api/mltd/v2/events?at=now", use_proxy=True
        )
    elif isinstance(time, datetime):
        t = datetime.now().astimezone().replace(microsecond=0).isoformat()
        return await network.fetch_json_data(
            f"https://api.matsurihi.me/api/mltd/v2/events?at={t}", use_proxy=True
        )
    return None
