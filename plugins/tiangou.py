from nonebot import on_command
from nonebot.plugin import PluginMetadata
import random

from ..libraries.assets import get_assets

__plugin_meta__ = PluginMetadata(
    name='舔狗语录',
    description='随机输出一条舔狗语录',
    usage='/<tiangou|舔狗>',
    config=None
)

tiangou_data: list[str] = [x[1] for x in get_assets('tiangou')]

# message
tiangou = on_command('tiangou', aliases={'舔狗'}, block=True)
@tiangou.handle()
async def _():
    await tiangou.finish(random.choice(tiangou_data))
