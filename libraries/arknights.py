import json
import random
from pathlib import Path
from typing import Tuple

from nonebot import logger

from . import render_by_browser

_arknights_assets_path = Path(__file__).parent.parent / 'assets' / 'arknights'
_arknights_all_characters: dict[str, dict] = {}
_arknights_gacha_operators: dict[int, list[dict]] = {}
_arknights_operator_professions = ['PIONEER', 'WARRIOR', 'SNIPER', 'CASTER', 'SUPPORT', 'MEDIC', 'SPECIAL', 'TANK']


def _load_arknights_data() -> None:
    global _arknights_all_characters

    # data version
    with (_arknights_assets_path / 'ArknightsGameResource' / 'version').open('r') as f:
        logger.info(f'ArknightsGameResource version: {f.read()}')

    # load characters
    with (_arknights_assets_path / 'ArknightsGameResource' / 'gamedata' / 'excel' / 'character_table.json')\
            .open('r', encoding='utf-8') as f:
        _arknights_all_characters = json.load(f)
        logger.info(f'arknights characters: {len(_arknights_all_characters)}')

    # generate gacha operators
    for k, v in _arknights_all_characters.items():
        if v['rarity'] not in _arknights_gacha_operators:
            _arknights_gacha_operators[v['rarity']] = []
        if v['profession'] in _arknights_operator_professions:
            _arknights_gacha_operators[v['rarity']].append(v)


_load_arknights_data()


async def generate_gacha() -> Tuple[bytes, list[dict]]:
    # get characters
    characters: list[dict] = []
    while len(characters) != 10:
        magic_number = random.random()
        if magic_number < 0.02:
            rarity = 5
        elif magic_number < 0.08:
            rarity = 4
        elif magic_number < 0.5:
            rarity = 3
        else:
            rarity = 2
        characters.append(random.choice(_arknights_gacha_operators[rarity]))

    # generate html
    with (_arknights_assets_path / 'gacha.html').open('r', encoding='utf-8') as f:
        generated_html = f.read().replace('{{CHARACTERS}}', json.dumps(characters))

    # render
    img = await render_by_browser.render_html(generated_html, _arknights_assets_path,
                                              viewport={'width': 1000, 'height': 500})
    return img, characters


async def main() -> None:
    img, _ = await generate_gacha()
    with open('out.png', 'wb') as f:
        f.write(img)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
