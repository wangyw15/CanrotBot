import json
import random
from typing import Tuple, Any

from nonebot import logger, get_driver
from sqlalchemy import select, insert
from sqlalchemy.orm import sessionmaker

from essentials.libraries import network, path, render_by_browser, database
from . import data

OPERATOR_PROFESSIONS = [
    "PIONEER",
    "WARRIOR",
    "SNIPER",
    "CASTER",
    "SUPPORT",
    "MEDIC",
    "SPECIAL",
    "TANK",
]
INDEX_TO_RARITY = [
    "one_star",
    "two_stars",
    "three_stars",
    "four_stars",
    "five_stars",
    "six_stars",
]
LOCAL_ASSETS_PATH = path.get_asset_path("arknights")
RESOURCE_URL = (
    "https://raw.githubusercontent.com/yuanyan3060/ArknightsGameResource/main/{}"
)

operators: dict[str, dict] = {}
gacha_operators: dict[int, list[dict]] = {}
resource_version: str = ""


@get_driver().on_startup
async def _load_data() -> None:
    global operators, resource_version

    resource_version = await network.fetch_text_data(
        RESOURCE_URL.format("version"), use_cache=True, use_proxy=True
    )

    # 数据版本
    logger.info(f"ArknightsGameResource version: {resource_version}")

    # 加载角色数据
    operators = await network.fetch_json_data(
        "gamedata/excel/character_table.json", use_cache=True, use_proxy=True
    )
    logger.info(f"Arknights characters count: {len(operators)}")

    # 生成寻访干员列表
    for k, v in operators.items():
        if v["rarity"] not in gacha_operators:
            gacha_operators[v["rarity"]] = []
        if v["profession"] not in OPERATOR_PROFESSIONS:
            continue
        if not v["itemObtainApproach"] == "招募寻访":
            continue
        gacha_operators[v["rarity"]].append(v)
    logger.info(f"arknights gacha operators: {len(gacha_operators)}")


async def generate_gacha(uid: int) -> Tuple[bytes, list[dict]]:
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
    query = select(data.Statistics).where(data.Statistics.user_id.is_(uid))
    current_statistics = session.execute(query).scalar_one_or_none()
    if current_statistics is None:
        session.execute(insert(data.Statistics).values(user_id=uid))
        session.commit()
        current_statistics = session.execute(query).scalar_one()

    # 寻访干员列表
    selected_operators: list[dict] = []

    # 六星概率提升
    possibility_offset: float = 0
    if current_statistics.last_six_star > 50:
        possibility_offset = (current_statistics.last_six_star - 50) * 0.02

    # 抽卡
    while len(selected_operators) != 10:
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
        selected_operators.append(random.choice(gacha_operators[rarity]))

    # 更新统计数据
    # 是否抽到六星
    got_ssr = False

    # 抽卡次数+10
    current_statistics.times += 10

    # 统计寻访结果
    for operator in selected_operators:
        if operator["rarity"] == 5:
            got_ssr = True
        setattr(
            current_statistics,
            INDEX_TO_RARITY[operator["rarity"]],
            getattr(current_statistics, INDEX_TO_RARITY[operator["rarity"]]) + 1,
        )

    # 上次抽到六星
    if got_ssr:
        current_statistics.last_six_star = 0
    else:
        current_statistics.last_six_star += 10

    # 寻访历史
    simple_operators: list[dict[str, Any]] = []
    for i in selected_operators:
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
    with (LOCAL_ASSETS_PATH / "gacha.html").open("r", encoding="utf-8") as f:
        generated_html = f.read().replace(
            "'{{DATA_HERE}}'", json.dumps(operators, ensure_ascii=False)
        )

    # 生成图片
    img = await render_by_browser.render_html(
        generated_html,
        LOCAL_ASSETS_PATH,
        viewport={"width": 1000, "height": 500},
    )
    return img, selected_operators
