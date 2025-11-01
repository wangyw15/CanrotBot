import random

from jinja2 import Template

from canrotbot.libraries import arknights as libarknights
from .. import fortune


async def _generate_arknights_html(title: str, content: str) -> str:
    rarity = random.choice(list(libarknights.gacha_operators.keys()))
    operator: dict = random.choice(libarknights.gacha_operators[rarity])
    with (fortune.ASSET_PATH / "template" / "arknights.jinja").open(
        "r", encoding="utf-8"
    ) as f:
        template: Template = Template(f.read())
    return template.render(title=title, content=content, resource_key=operator["id"])


fortune.register_theme(
    "arknights",
    _generate_arknights_html,
    ["明日方舟", "方舟", "鹰角", "Arknights", "舟游"],
)
