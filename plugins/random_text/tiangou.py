from nonebot import on_command
from nonebot.plugin import PluginMetadata
import random

from . import get_data

__plugin_meta__ = PluginMetadata(
    name='舔狗语录',
    description='随机输出一条舔狗语录',
    usage='/<tiangou|舔狗>',
    config=None
)

_tiangou_data: list[str] = get_data('tiangou')

# message
_tiangou_handler = on_command('tiangou', aliases={'舔狗'}, block=True)
@_tiangou_handler.handle()
async def _():
    await _tiangou_handler.finish(random.choice(_tiangou_data))
