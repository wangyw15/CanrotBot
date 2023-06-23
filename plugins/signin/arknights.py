import random

from . import fortune
from ..arknights import arknights


async def _generate_arknights_html() -> str:
    rarity = random.choice(list(arknights.arknights_gacha_operators.keys()))
    operator: dict = random.choice(arknights.arknights_gacha_operators[rarity])
    operator_prefab_key = operator['phases'][0]['characterPrefabKey']
    with (fortune.fortune_assets_path / 'template' / 'arknights.html').open('r', encoding='utf-8') as f:
        return f.read().replace('{{resource_key}}', operator_prefab_key)


fortune.register_theme('arknights', _generate_arknights_html, ["明日方舟", "方舟", "鹰角", "Arknights", "舟游"])
