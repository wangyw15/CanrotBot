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
        if v['profession'] not in _arknights_operator_professions:
            continue
        if not v['itemObtainApproach'] == '招募寻访':
            continue
        _arknights_gacha_operators[v['rarity']].append(v)
    logger.info(f'arknights gacha operators: {len(_arknights_gacha_operators)}')


_load_arknights_data()


async def generate_gacha(last_5_times: int = 0) -> Tuple[bytes, list[dict]]:
    """
    明日方舟十连抽卡

    :param last_5_times: 距离上次抽卡出 6 星的次数
    """
    # 寻访干员列表
    characters: list[dict] = []
    # 六星概率提升
    possibility_offset: float = 0
    if last_5_times > 50:
        possibility_offset = (last_5_times - 50) * 0.02
    # 抽卡
    while len(characters) != 10:
        magic_number = random.random()
        # 决定等级
        if magic_number < 0.02 + possibility_offset:
            rarity = 5
            possibility_offset = 0  # 抽到六星之后重置概率提升
        elif magic_number < 0.10 + possibility_offset:
            rarity = 4
        elif magic_number < 0.60 + possibility_offset:
            rarity = 3
        else:
            rarity = 2
        characters.append(random.choice(_arknights_gacha_operators[rarity]))

    # 生成 html
    with (_arknights_assets_path / 'gacha.html').open('r', encoding='utf-8') as f:
        generated_html = f.read().replace("'{{DATA_HERE}}'", json.dumps(characters, ensure_ascii=False))

    # 生成图片
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
