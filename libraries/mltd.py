import difflib
import json
import random
from datetime import datetime
from typing import Literal, Tuple

from essentials.libraries import asset, render_by_browser, util

_mltd_assets_path = asset.get_assets_path('mltd')
_cards: list[dict] = []
_cards_zh: list[dict] = []
_cards_last_fetch: datetime | None = None
_cards_for_gasha: dict[int, list[dict]] = {}


async def load_cards(force_reload: bool = False) -> None:
    global _cards, _cards_zh, _cards_last_fetch, _cards_for_gasha
    if force_reload or not _cards or not _cards_zh or not _cards_last_fetch \
            or (datetime.now() - _cards_last_fetch).total_seconds() > 3600*24:
        _cards = await util.fetch_json_data(
            'https://api.matsurihi.me/api/mltd/v2/cards'
            '?includeCostumes=true&includeParameters=true&includeLines=true&includeSkills=true&includeEvents=true')
        _cards_zh = await util.fetch_json_data(
            'https://api.matsurihi.me/api/mltd/v2/zh/cards'
            '?includeCostumes=true&includeParameters=true&includeLines=true&includeSkills=true&includeEvents=true')
        _cards_last_fetch = datetime.now()
        # 生成卡池
        _cards_for_gasha = {}
        for card in _cards:
            if card['rarity'] == 1 or card['exType'] != 0:
                continue
            if card['rarity'] not in _cards_for_gasha:
                _cards_for_gasha[card['rarity']] = []
            _cards_for_gasha[card['rarity']].append(card)


async def get_cards() -> list[dict]:
    await load_cards()
    return _cards


async def search_card(keyword: str, force_jp: bool = False) -> dict:
    await load_cards()
    best = 0.0
    ret = {}
    # 优先搜索中文内容
    if not force_jp:
        for card in _cards_zh:
            ratio = difflib.SequenceMatcher(None, keyword, card['name']).quick_ratio()
            if ratio > best:
                best = ratio
                ret = card
        if keyword in ret['name']:
            return ret
    # 搜索日文内容
    for card in _cards:
        ratio = difflib.SequenceMatcher(None, keyword, card['name']).quick_ratio()
        if ratio > best:
            best = ratio
            ret = card
    return ret


async def generate_card_info_image(card: dict) -> bytes:
    with (_mltd_assets_path / 'card_info.html').open('r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace("'{DATA_HERE}'", json.dumps(card))
    return await render_by_browser.render_html(html, _mltd_assets_path, viewport={'width': 1280, 'height': 1000})


async def get_events(time: Literal['now'] | datetime = 'now') -> list[dict] | None:
    if time == 'now':
        return await util.fetch_json_data(f'https://api.matsurihi.me/api/mltd/v2/events?at=now')
    elif isinstance(time, datetime):
        t = datetime.now().astimezone().replace(microsecond=0).isoformat()
        return await util.fetch_json_data(f'https://api.matsurihi.me/api/mltd/v2/events?at={t}')


async def gasha() -> Tuple[bytes, list[dict]]:
    await load_cards()
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
    with (_mltd_assets_path / 'gasha.html').open('r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace("'{DATA_HERE}'", json.dumps(cards))
    img = await render_by_browser.render_html(html, _mltd_assets_path, viewport={'width': 1920, 'height': 1080})
    return img, cards


async def main():
    await gasha()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
