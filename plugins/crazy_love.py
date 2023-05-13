from nonebot import on_command
from nonebot.plugin import PluginMetadata
import random

from ..libraries.assets import get_assets

__plugin_meta__ = PluginMetadata(
    name='发癫',
    description='随机输出一偏发癫文',
    usage='/<crazy_love|crazy-love|发癫|发电>',
    config=None
)

crazy_love_data: list[str] = [x[1] for x in get_assets('crazy_love')]

# message
crazy_love = on_command('crazy-love', aliases={'发癫', '发电', 'crazy_love'}, block=True)
@crazy_love.handle()
async def _():
    await crazy_love.finish(random.choice(crazy_love_data))
