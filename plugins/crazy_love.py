from nonebot import on_command
from nonebot.plugin import PluginMetadata
import random

from ..libraries import random_text

__plugin_meta__ = PluginMetadata(
    name='发癫',
    description='随机输出一偏发癫文',
    usage='/<crazy_love|crazy-love|发癫|发电>',
    config=None
)

_crazy_love_data: list[str] = random_text.get_data('crazy_love')

# message
_crazy_love_handler = on_command('crazy-love', aliases={'发癫', '发电', 'crazy_love'}, block=True)
@_crazy_love_handler.handle()
async def _():
    await _crazy_love_handler.finish(random.choice(_crazy_love_data))
