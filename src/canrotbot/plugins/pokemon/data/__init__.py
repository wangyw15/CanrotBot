import json

from canrotbot.essentials.libraries import path

ASSET_PATH = path.get_asset_path("pokemon")


def get_pokemon_types() -> list[str]:
    """
    获取宝可梦属性列表

    :return: 宝可梦属性列表
    """
    with (ASSET_PATH / "types.json").open("r", encoding="utf-8") as f:
        return json.load(f)
