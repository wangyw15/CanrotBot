import json
import random

from nonebot import logger, get_driver
from sqlalchemy import insert, select

from essentials.libraries import network, path, render_by_browser, database
from .data import GachaHistory, GachaHistoryOperators
from .model import OperatorProfessions, GachaOperatorData, GachaStatistics

LOCAL_ASSETS_PATH = path.get_asset_path("arknights")
RESOURCE_URL = (
    "https://raw.githubusercontent.com/yuanyan3060/ArknightsGameResource/main/{}"
)

operators: dict[str, dict] = {}
gacha_operators: dict[int, list[GachaOperatorData]] = {}
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
        RESOURCE_URL.format("gamedata/excel/character_table.json"),
        use_cache=True,
        use_proxy=True,
    )
    logger.info(f"Arknights characters count: {len(operators)}")

    gacha_operator_count = 0
    # 生成寻访干员列表
    for operator_id, operator_data in operators.items():
        if operator_data["rarity"] not in gacha_operators:
            gacha_operators[operator_data["rarity"]] = []
        if operator_data["profession"] not in OperatorProfessions:
            continue
        if operator_data["itemObtainApproach"] != "招募寻访":
            continue
        gacha_operators[operator_data["rarity"]].append(
            {
                "id": operator_id,
                "name": operator_data["name"],
                "rarity": operator_data["rarity"],
                "profession": operator_data["profession"],
            }
        )
        gacha_operator_count += 1
    logger.info(f"Arknights gacha operators: {gacha_operator_count}")


def get_last_six_star(uid: int) -> int:
    """
    获取用户最近100次抽卡中抽到六星的次数

    :param uid: 用户id

    :return: 次数
    """
    with database.get_session().begin() as session:
        gacha_ids = (
            session.execute(
                select(GachaHistory.id)
                .where(GachaHistory.user_id.is_(uid))
                .order_by(GachaHistory.time.desc)
                .limit(100)
            )
            .scalars()
            .all()
        )

        if not gacha_ids:
            return 0

        operator_rarities = (
            session.execute(
                select(GachaHistoryOperators.rarity)
                .where(GachaHistoryOperators.gacha_id.in_(gacha_ids))
                .order_by(GachaHistoryOperators.id.desc)
            )
            .scalars()
            .all()
        )
        result = 0
        for rarity in operator_rarities:
            if rarity == 5:
                break
            result += 1
        return result


def generate_gacha(last_six_star: int, count: int = 10) -> list[GachaOperatorData]:
    """
    生成明日方舟十连寻访

    :param last_six_star: 用户最近100次抽卡中抽到六星的次数
    :param count: 寻访个数

    :return: 干员列表
    """
    possibility_offset: float = 0.0
    if last_six_star > 50:
        possibility_offset = (last_six_star - 50) * 0.02

    # 寻访干员列表
    selected_operators: list[GachaOperatorData] = []

    # 抽卡
    for i in range(count):
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

    return selected_operators


def generate_gacha_text(selected_operators: list[GachaOperatorData]) -> str:
    """
    生成明日方舟寻访结果文本

    :param selected_operators: 干员列表

    :return: 文本
    """
    ret = "明日方舟寻访结果: \n"
    for operator in selected_operators:
        ret += f"{operator['rarity'] + 1}星 {operator['name']}\n"
    return ret


async def generate_gacha_image(selected_operators: list[GachaOperatorData]) -> bytes:
    """
    生成明日方舟寻访结果图片

    :param selected_operators: 干员列表

    :return: 图片
    """
    # 生成 html
    with (LOCAL_ASSETS_PATH / "gacha.html").open("r", encoding="utf-8") as f:
        generated_html = f.read().replace(
            "'{{DATA_HERE}}'", json.dumps(selected_operators, ensure_ascii=False)
        )

    # 生成图片
    return await render_by_browser.render_html(
        generated_html,
        LOCAL_ASSETS_PATH,
        viewport={"width": 1000, "height": 500},
    )


def save_gacha_history(uid: int, selected_operators: list[GachaOperatorData]) -> None:
    """
    保存抽卡历史

    :param uid: 用户id
    :param selected_operators: 干员列表
    """
    with database.get_session().begin() as session:
        gacha_history = GachaHistory(user_id=uid)
        session.add(gacha_history)
        session.flush()

        for operator in selected_operators:
            session.execute(
                insert(GachaHistoryOperators).values(
                    gacha_id=gacha_history.id,
                    name=operator["name"],
                    operator_id=operator["id"],
                    rarity=operator["rarity"],
                )
            )
        session.commit()


def get_gacha_statistics(uid: int) -> GachaStatistics:
    """
    获取用户抽卡统计

    :param uid: 用户id

    :return: 统计数据
    """
    statistics: GachaStatistics = {
        "user_id": uid,
        "times": 0,
        "one_star": 0,
        "two_stars": 0,
        "three_stars": 0,
        "four_stars": 0,
        "five_stars": 0,
        "six_stars": 0,
        "last_six_star": 0,
    }
    with database.get_session().begin() as session:
        gacha_ids = (
            session.execute(
                select(GachaHistory.id)
                .where(GachaHistory.user_id.is_(uid))
                .order_by(GachaHistory.time.desc)
                .limit(100)
            )
            .scalars()
            .all()
        )

        if not gacha_ids:
            return statistics

        history_operators = (
            session.execute(
                select(GachaHistoryOperators)
                .where(GachaHistoryOperators.gacha_id.in_(gacha_ids))
                .order_by(GachaHistoryOperators.id.desc)
            )
            .scalars()
            .all()
        )

        # 统计数据
        last_six_star = 0
        got_six = False
        for i in history_operators:
            # 计算上次抽到六星的次数
            if not got_six:
                if i.rarity == 5:
                    got_six = True
                else:
                    last_six_star += 1
            statistics["times"] += 1
            if i.rarity == 0:
                statistics["one_star"] += 1
            elif i.rarity == 1:
                statistics["two_stars"] += 1
            elif i.rarity == 2:
                statistics["three_stars"] += 1
            elif i.rarity == 3:
                statistics["four_stars"] += 1
            elif i.rarity == 4:
                statistics["five_stars"] += 1
            elif i.rarity == 5:
                statistics["six_stars"] += 1
        statistics["last_six_star"] = last_six_star

        return statistics
