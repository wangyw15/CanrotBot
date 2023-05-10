from nonebot import on_command
from nonebot.plugin import PluginMetadata
import random

from ..data import get_data

__plugin_meta__ = PluginMetadata(
    name='浅草寺',
    description='赛博浅草寺',
    usage='/<kuji|浅草寺>',
    config=None
)

kuji_data: list[str] = [x[1] for x in get_data('kuji')]

# message
kuji = on_command('kuji', aliases={'浅草寺'}, block=True)
@kuji.handle()
async def _():
    await kuji.finish(random.choice(kuji_data))
