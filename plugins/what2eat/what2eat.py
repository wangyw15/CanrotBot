import json
import random
from pathlib import Path

# 加载数据
with (Path(__file__).parent.parent.parent / "assets" / "what2eat.json").open('r', encoding='utf-8') as f:
    _what2eat_data: dict[str, list[dict]] = json.load(f)


def get_drink_by_brand(brand: str) -> str:
    """
    根据品牌随机获取一种饮料

    :param brand: 品牌
    :return: 饮料名称
    """
    drinks: list[str] = []
    for i in _what2eat_data['drink']:
        if i['brand'].lower() == brand.lower():
            drinks.append(i['name'])
    if drinks:
        return random.choice(drinks)
    else:
        return ''
