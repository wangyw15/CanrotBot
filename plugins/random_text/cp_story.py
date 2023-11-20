import random

from arclet.alconna import Alconna, Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Query, AlconnaQuery

from . import get_data

__plugin_meta__ = PluginMetadata(
    name='CP',
    description='生成cp文',
    usage='/<cp|cp文> <攻> <受>',
    config=None
)

_cp_stories: list[dict[str, str]] = get_data('cp_story')
_cp_handler = on_alconna(Alconna(
    'cp',
    Args['s', str, '']['m', str, '']
), block=True)


@_cp_handler.handle()
async def _(s: Query[str] = AlconnaQuery('s', ''), m: Query[str] = AlconnaQuery('m', '')):
    s = s.result.strip()
    m = m.result.strip()
    data = random.choice(_cp_stories)
    await _cp_handler.finish(
        data['story'].format(s=s if s else '小攻', m=m if m else '小受'))
