import asyncio
import json
import random
from datetime import timedelta
from typing import Tuple

from nonebot import logger
from sqlalchemy import select, insert
from sqlalchemy.orm import sessionmaker

from essentials.libraries import render_by_browser
from storage import database, asset
from . import data

_arknights_all_characters: dict[str, dict] = {}
arknights_gacha_operators: dict[int, list[dict]] = {}
_arknights_operator_professions = [
    "PIONEER",
    "WARRIOR",
    "SNIPER",
    "CASTER",
    "SUPPORT",
    "MEDIC",
    "SPECIAL",
    "TANK",
]
_arknights_local_assets = asset.AssetManager("arknights")
_arknights_remote_assets = asset.GithubAssetManager(
    "yuanyan3060/ArknightsGameResource", "main", expire=timedelta(days=7)
)
_number_to_rarity = [
    "one_star",
    "two_stars",
    "three_stars",
    "four_stars",
    "five_stars",
    "six_stars",
]


# TODO 改为在线获取资源
async def _init() -> None:
    global _arknights_all_characters

    # 数据版本
    logger.info(
        f"ArknightsGameResource version: {await _arknights_remote_assets('version').text()}"
    )

    # 加载角色数据
    _arknights_all_characters = await _arknights_remote_assets(
        "gamedata/excel/character_table.json"
    ).json()
    logger.info(f"Arknights characters: {len(_arknights_all_characters)}")

    # generate gacha operators
    for k, v in _arknights_all_characters.items():
        if v["rarity"] not in arknights_gacha_operators:
            arknights_gacha_operators[v["rarity"]] = []
        if v["profession"] not in _arknights_operator_professions:
            continue
        if not v["itemObtainApproach"] == "招募寻访":
            continue
        arknights_gacha_operators[v["rarity"]].append(v)
    logger.info(f"arknights gacha operators: {len(arknights_gacha_operators)}")


with asyncio.Runner() as runner:
    runner.run(_init())


async def generate_gacha(uid: str) -> Tuple[bytes, list[dict]]:
    """
    明日方舟十连抽卡，并自动更新统计数据

    :param uid: uid

    :return: 图片, 干员列表
    """
    # TODO 分离图片生成
    # TODO 分离数据库操作
    maker = sessionmaker(bind=database.get_engine(), expire_on_commit=False)
    session = maker()

    # 获取当前统计数据
    query = select(data.Statistics).where(data.Statistics.user_id == uid)
    current_statistics = session.execute(query).scalar_one_or_none()
    if current_statistics is None:
        session.execute(insert(data.Statistics).values(user_id=uid))
        session.commit()
        current_statistics = session.execute(query).scalar_one()

    # 寻访干员列表
    operators: list[dict] = []

    # 六星概率提升
    possibility_offset: float = 0
    if current_statistics.last_six_star > 50:
        possibility_offset = (current_statistics.last_six_star - 50) * 0.02

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
    # 是否抽到六星
    got_ssr = False

    # 抽卡次数+10
    current_statistics.times += 10

    # 统计寻访结果
    for operator in operators:
        if operator["rarity"] == 5:
            got_ssr = True
        setattr(
            current_statistics,
            _number_to_rarity[operator["rarity"]],
            getattr(current_statistics, _number_to_rarity[operator["rarity"]]) + 1,
        )

    # 上次抽到六星
    if got_ssr:
        current_statistics.last_six_star = 0
    else:
        current_statistics.last_six_star += 10

    # 寻访历史
    simple_operators: list[dict[str]] = []
    for i in operators:
        simple_operators.append({"name": i["name"], "rarity": i["rarity"]})

    # 保存数据
    session.execute(
        insert(data.History).values(
            user_id=uid, operators=json.dumps(simple_operators, ensure_ascii=False)
        )
    )
    session.commit()
    session.close()

    # 生成 html
    with _arknights_local_assets("gacha.html").open("r", encoding="utf-8") as f:
        generated_html = f.read().replace(
            "'{{DATA_HERE}}'", json.dumps(operators, ensure_ascii=False)
        )

    # 生成图片
    img = await render_by_browser.render_html(
        generated_html,
        _arknights_local_assets(),
        viewport={"width": 1000, "height": 500},
    )
    return img, operators


async def main() -> None:
    img, _ = await generate_gacha("console_0")
    with open("out.png", "wb") as f:
        f.write(img)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
