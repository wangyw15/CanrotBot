import json
import random
from datetime import datetime
from typing import Tuple

from nonebot import logger

from essentials.libraries import render_by_browser

from storage import database, asset
from sqlalchemy import select, update, insert
from . import data

_arknights_all_characters: dict[str, dict] = {}
arknights_gacha_operators: dict[int, list[dict]] = {}
_arknights_operator_professions = ['PIONEER', 'WARRIOR', 'SNIPER', 'CASTER', 'SUPPORT', 'MEDIC', 'SPECIAL', 'TANK']
_arknights_assets = asset.Asset('arknights')
_number_to_rarity = ['one_star', 'two_stars', 'three_stars', 'four_stars', 'five_stars', 'six_stars']


def _init() -> None:
    global _arknights_all_characters
    # data version
    with (_arknights_assets() / 'ArknightsGameResource' / 'version').open('r') as f:
        logger.info(f'ArknightsGameResource version: {f.read()}')

    # load characters
    with (_arknights_assets() / 'ArknightsGameResource' / 'gamedata' / 'excel' / 'character_table.json')\
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


_init()


def get_gacha_data(uid: str) -> data.Statistics:
    """
    获取抽卡统计

    :param uid: uid

    :return: 统计数据
    """
    with database.get_session().begin() as session:
        query = select(data.Statistics).where(data.Statistics.user_id == uid)
        if session.execute(query).first() is None:
            session.add(data.Statistics(uid=uid))
        return session.execute(query).scalar_one()


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
    if get_gacha_data(uid).last_six_star > 50:
        possibility_offset = (get_gacha_data(uid).last_six_star - 50) * 0.02
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
    current_result.times += 10
    # 统计寻访结果
    for operator in operators:
        if operator['rarity'] == 5:
            got_ssr = True
        setattr(current_result, _number_to_rarity[operator['rarity']],
                getattr(current_result, _number_to_rarity[operator['rarity']]) + 1)
    # 上次抽到六星
    if got_ssr:
        current_result.last_six_star = 0
    else:
        current_result.last_six_star += 10
    # 寻访历史
    simple_operators: list[dict[str]] = []
    for i in operators:
        simple_operators.append({
            'name': i['name'],
            'rarity': i['rarity']
        })
    # 保存数据
    with database.get_session().begin() as session:
        session.execute(update(data.Statistics).where(data.Statistics.user_id == uid).values(
            three_stars=current_result.three_stars,
            four_stars=current_result.four_stars,
            five_stars=current_result.five_stars,
            six_stars=current_result.six_stars,
            times=current_result.times,
            last_six_star=current_result.last_six_star
        ))
        session.execute(insert(data.History).values(
            uid=uid,
            operators=json.dumps(simple_operators, ensure_ascii=False)
        ))
        session.commit()

    # 生成 html
    with _arknights_assets('gacha.html').open('r', encoding='utf-8') as f:
        generated_html = f.read().replace("'{{DATA_HERE}}'", json.dumps(operators, ensure_ascii=False))

    # 生成图片
    img = await render_by_browser.render_html(generated_html, _arknights_assets(),
                                              viewport={'width': 1000, 'height': 500})
    return img, operators


async def main() -> None:
    img, _ = await generate_gacha('console_0')
    with open('out.png', 'wb') as f:
        f.write(img)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
