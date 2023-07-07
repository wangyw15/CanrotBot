import random

from essentials.libraries import util
from .. import fortune

util.require_plugin('mltd')
from ...mltd import mltd


async def _generate_mltd_html() -> str:
    card = random.choice(await mltd.get_cards())
    with (fortune.fortune_assets_path / 'template' / 'mltd.html').open('r', encoding='utf-8') as f:
        return f.read().replace('{{resource_key}}', card['resourceId'])


fortune.register_theme('mltd', _generate_mltd_html, ["麻辣土豆", "百万现场", "百万", "偶像大师百万现场"])
