from nonebot import get_driver, logger

from canrotbot.essentials.libraries import network

from .model import GachaOperatorData, OperatorProfessions

RESOURCE_URL = (
    "https://raw.githubusercontent.com/yuanyan3060/ArknightsGameResource/main/{}"
)
operators: dict[str, dict] = {}
gacha_operators: dict[int, list[GachaOperatorData]] = {}
resource_version: str = ""


@get_driver().on_startup
async def _on_startup() -> None:
    try:
        await load_arknights_data()
    except Exception as e:
        logger.error(f"Failed to load Arknights data")
        logger.exception(e)


async def load_arknights_data() -> None:
    global operators, resource_version

    resource_version = await network.fetch_text_data(
        RESOURCE_URL.format("version"), use_proxy=True
    )

    # 数据版本
    logger.info(f"ArknightsGameResource version: {resource_version}")

    # 加载角色数据
    operators = await network.fetch_json_data(
        RESOURCE_URL.format("gamedata/excel/character_table.json"),
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
