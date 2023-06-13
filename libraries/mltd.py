import difflib
import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from . import render_by_browser
from ..adapters import unified

_cards: list[dict] = []
_cards_zh: list[dict] = []
_cards_last_fetch: datetime | None = None
_card_info_template_path = Path(__file__).parent.parent / 'assets' / 'mltd' / 'card_info.html'


async def _load_cards(force_reload: bool = False) -> None:
    global _cards, _cards_zh, _cards_last_fetch
    if force_reload or not _cards or not _cards_zh or not _cards_last_fetch \
            or (datetime.now() - _cards_last_fetch).total_seconds() > 3600:
        _cards = await unified.util.fetch_json_data(
            'https://api.matsurihi.me/api/mltd/v2/cards?includeCostumes=true&includeParameters=true&includeLines=true&includeSkills=true&includeEvents=true')
        _cards_zh = await unified.util.fetch_json_data(
            'https://api.matsurihi.me/api/mltd/v2/zh/cards?includeCostumes=true&includeParameters=true&includeLines=true&includeSkills=true&includeEvents=true')
        _cards_last_fetch = datetime.now()


async def search_card(keyword: str, force_jp: bool = False) -> dict:
    await _load_cards()
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
    with _card_info_template_path.open('r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace("'{DATA_HERE}'", json.dumps(card))
    return await render_by_browser.render_html(html, _card_info_template_path.parent,
                                               viewport={'width': 1280, 'height': 1000})


async def get_events(time: Literal['now'] | datetime = 'now') -> list[dict] | None:
    if time == 'now':
        return await unified.util.fetch_json_data(f'https://api.matsurihi.me/api/mltd/v2/events?at=now')
    elif isinstance(time, datetime):
        t = datetime.now().astimezone().replace(microsecond=0).isoformat()
        return await unified.util.fetch_json_data(f'https://api.matsurihi.me/api/mltd/v2/events?at={t}')


async def main():
    with open('out.png', 'wb') as f:
        f.write(await generate_card_info_image(await search_card('追憶のサンドグラス　星井美希', True)))


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
