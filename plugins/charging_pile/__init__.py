from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from . import charging_pile

__plugin_meta__ = PluginMetadata(
    name='找充电桩',
    description='电瓶车没电了！我应该去哪充电？（仅限上大）',
    usage='/charge',
    config=None
)


_charging_pile_handler = on_command('charge', aliases={'充电', '充电桩'}, block=True)


@_charging_pile_handler.handle()
async def _():
    await _charging_pile_handler.send('正在查询喵~')
    await _charging_pile_handler.finish(await charging_pile.generate_message('上海大学'))
