import json
import random

from sqlalchemy import insert

from canrotbot.essentials.libraries import database, path, render_by_browser
from .bestdori import band_character, card, gacha, util
from .data import GachaHistory, GachaHistoryCards

ASSET_PATH = path.get_asset_path("bang_dream")


async def gacha10(gacha_id: int, language: str = "cn") -> dict[str, dict]:
    """
    一发十连

    :params gacha_id: 卡池ID
    :params language: 语言

    :return: 抽卡结果, 语言
    """
    # 获取卡池信息
    data = await gacha.get_gacha_info(gacha_id)

    # 获取权重
    rates: dict[str]
    rates, _ = util.get_content_by_language(data["rates"], language)

    # 计算总概率和三星及以上概率
    total_rate = 0
    better_than_three_star_rate = 0
    for k, v in rates.items():
        total_rate += v["rate"]
        if int(k) >= 3:
            better_than_three_star_rate += v["rate"]

    # 卡池内的卡片信息
    cards: dict[str]
    cards, _ = util.get_content_by_language(data["details"], language)

    # 抽卡结果
    result_card_ids = []
    # 保底
    three_star_appeared = False

    while len(result_card_ids) < 10:
        # 随机概率
        rate = random.randint(1, int(total_rate * 10)) / 10
        # 计算稀有度
        rarity = "1"
        for k, v in rates.items():
            if rate <= v["rate"]:
                rarity = k
                break
            rate -= v["rate"]

        # 保底三星及以上
        three_star_appeared = int(rarity) >= 3 or three_star_appeared
        if len(result_card_ids) == 9 and not three_star_appeared:
            rarity = "3"
            rate = random.randint(1, int(better_than_three_star_rate * 10)) / 10
            for j in ["3", "4", "5"]:
                if rate <= rates[j]["rate"]:
                    rarity = j
                    break
                rate -= rates[j]["rate"]

        # 随机卡片
        weight = random.randint(1, rates[rarity]["weightTotal"])
        card_id = "1"
        for k, v in cards.items():
            if str(v["rarityIndex"]) != rarity:
                continue
            if weight <= v["weight"]:
                card_id = k
                break
            weight -= v["weight"]
        result_card_ids.append(card_id)

    # 获取卡片信息
    result_cards = {}
    for card_id in result_card_ids:
        result_cards[card_id] = await card.get_card_info(card_id)

    return result_cards


async def generate_data_for_image(gacha_data: dict[str, dict]) -> list[dict]:
    result = []
    characters: dict[str] = await band_character.get_character_list()
    for card_id, card_data in gacha_data.items():
        result.append(
            {
                "id": card_id,
                "band": characters[str(card_data["characterId"])]["bandId"],
                "rarity": card_data["rarity"],
                "attribute": card_data["attribute"],
                "resource": card_data["resourceSetName"],
            }
        )
    return result


async def generate_image(gacha_data: dict[str, dict]) -> bytes:
    """
    生成抽卡图片

    :params gacha_data: 抽卡数据

    :return: 图片
    """
    data = await generate_data_for_image(gacha_data)
    generated_html = (
        (ASSET_PATH / "gacha.html")
        .read_text(encoding="utf-8")
        .replace("'{{DATA_HERE}}'", json.dumps(data, ensure_ascii=False))
    )

    return await render_by_browser.render_html(
        generated_html, ASSET_PATH, viewport={"width": 1920, "height": 1080}
    )


async def generate_text(gacha_data: dict[str, dict], language: str = "cn") -> str:
    """
    生成抽卡文字

    :params gacha_data: 抽卡数据
    :params language: 语言

    :return: 文字
    """
    result = ""
    characters: dict[str] = await band_character.get_character_list()
    for card_id, card_data in gacha_data.items():
        card_name, _ = util.get_content_by_language(card_data["prefix"], language)
        character_name, _ = util.get_content_by_language(
            characters[str(card_data["characterId"])]["characterName"], language
        )
        result += f'{card_data["rarity"]}★ {character_name} - {card_name}\n'
    return result.strip()


async def get_gacha_name(gacha_id: int, language: str = "cn") -> str:
    """
    获取卡池名称

    :params gacha_id: 卡池ID
    :params language: 语言

    :return: 卡池名称
    """
    data = await gacha.get_gacha_info(gacha_id)
    title, _ = util.get_content_by_language(data["gachaName"], language)
    return title


def save_gacha_history(
    user_id: int, gacha_id: int, cards: dict[str, dict], language: str = "cn"
):
    """
    保存抽卡记录

    :params user_id: 用户
    :params gacha_id: 卡池
    :params cards: 卡片
    """
    with database.get_session().begin() as session:
        history = GachaHistory(user_id=user_id, gacha_id=gacha_id)
        session.add(history)
        session.flush()

        for card_id, card_data in cards.items():
            session.execute(
                insert(GachaHistoryCards).values(
                    gacha_history_id=history.id,
                    character_id=card_data["characterId"],
                    name=util.get_content_by_language(card_data["prefix"], language)[0],
                    card_id=card_id,
                    rarity=card_data["rarity"],
                    attribute=card_data["attribute"],
                )
            )
        session.commit()
