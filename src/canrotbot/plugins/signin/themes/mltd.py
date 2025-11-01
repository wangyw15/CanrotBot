import random

from jinja2 import Template

import canrotbot.libraries.mltd as libmltd
from .. import fortune


async def _generate_mltd_html(title: str, content: str) -> str:
    card = random.choice(libmltd.get_cards())
    with (fortune.ASSET_PATH / "template" / "mltd.jinja").open(
        "r", encoding="utf-8"
    ) as f:
        template: Template = Template(f.read())
    return template.render(title=title, content=content, resource_key=card["resourceId"])


fortune.register_theme(
    "mltd", _generate_mltd_html, ["麻辣土豆", "百万现场", "百万", "偶像大师百万现场"]
)
