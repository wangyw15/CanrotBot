import random

from nonebot import require

from .. import fortune

require("mltd")
from plugins.mltd import mltd


def _generate_mltd_html() -> str:
    card = random.choice(mltd.get_cards())
    with (fortune.ASSET_PATH / "template" / "mltd.html").open(
        "r", encoding="utf-8"
    ) as f:
        return f.read().replace("{{resource_key}}", card["resourceId"])


fortune.register_theme(
    "mltd", _generate_mltd_html, ["麻辣土豆", "百万现场", "百万", "偶像大师百万现场"]
)
