import json
import random
from datetime import datetime
from pathlib import Path
from typing import Tuple

from nonebot import logger

from essentials.libraries import render_by_browser, storage

_arknights_assets_path = Path(__file__).parent.parent.parent / 'assets' / 'arknights'
_arknights_all_characters: dict[str, dict] = {}
arknights_gacha_operators: dict[int, list[dict]] = {}
_arknights_operator_professions = ['PIONEER', 'WARRIOR', 'SNIPER', 'CASTER', 'SUPPORT', 'MEDIC', 'SPECIAL', 'TANK']
_arknights_data_path = storage.get_path('arknights')
_arknights_gacha_result = storage.PersistentData[dict[str]]('arknights')


def _init() -> None:
    global _arknights_gacha_result, _arknights_all_characters
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
        if v['rarity'] not in arknights_gacha_operators:
            arknights_gacha_operators[v['rarity']] = []
        if v['profession'] not in _arknights_operator_professions:
            continue
        if not v['itemObtainApproach'] == '招募寻访':
            continue
        arknights_gacha_operators[v['rarity']].append(v)
    logger.info(f'arknights gacha operators: {len(arknights_gacha_operators)}')

    # 加载抽卡历史数据
    if not _arknights_data_path.exists():
        _arknights_data_path.mkdir(parents=True, exist_ok=True)
    for i in _arknights_data_path.iterdir():
        if i.is_file() and i.suffix == '.json':
            _arknights_gacha_result[i.stem] = json.loads(i.read_text(encoding='utf-8'))


_init()


def get_gacha_data(uid: str) -> dict[str]:
    """
    获取抽卡统计

    :param uid: uid

    :return: 统计数据
    """
    if uid not in _arknights_gacha_result:
        return {'5': 0, '4': 0, '3': 0, '2': 0, 'times': 0, 'last_5': 0, 'history': []}
    return _arknights_gacha_result[uid]


async def generate_gacha(uid: str) -> Tuple[bytes, list[dict]]:
    """
    明日方舟十连抽卡，并自动更新统计数据

    :param uid: uid

    :return: 图片, 干员列表
    """
    # 寻访干员列表
    operators: list[dict] = []
    # 六星概率提升
    possibility_offset: float = 0
    if get_gacha_data(uid)['last_5'] > 50:
        possibility_offset = (get_gacha_data(uid)['last_5'] - 50) * 0.02
    # 抽卡
    while len(operators) != 10:
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
        operators.append(random.choice(arknights_gacha_operators[rarity]))

    # 更新统计数据
    current_result = get_gacha_data(uid)
    # 是否抽到六星
    got_ssr = False
    # 抽卡次数+10
    current_result['times'] += 10
    # 统计寻访结果
    for operator in operators:
        if operator['rarity'] == 5:
            got_ssr = True
        current_result[str(operator['rarity'])] += 1
    # 上次抽到六星
    if got_ssr:
        current_result['last_5'] = 0
    else:
        current_result['last_5'] += 10
    # 寻访历史
    simple_operators: list[dict[str]] = []
    for i in operators:
        simple_operators.append({
            'name': i['name'],
            'rarity': i['rarity']
        })
    current_result['history'].append({
        'time': datetime.now().astimezone().isoformat(),
        'operators': simple_operators
    })
    # 保存数据
    _arknights_gacha_result[uid] = current_result

    # 生成 html
    with (_arknights_assets_path / 'gacha.html').open('r', encoding='utf-8') as f:
        generated_html = f.read().replace("'{{DATA_HERE}}'", json.dumps(operators, ensure_ascii=False))

    # 生成图片
    img = await render_by_browser.render_html(generated_html, _arknights_assets_path,
                                              viewport={'width': 1000, 'height': 500})
    return img, operators


async def main() -> None:
    img, _ = await generate_gacha('console_0')
    with open('out.png', 'wb') as f:
        f.write(img)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
