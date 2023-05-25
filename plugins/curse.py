from nonebot import on_command
from nonebot.plugin import PluginMetadata
import random

from ..libraries.assets import get_assets

__plugin_meta__ = PluginMetadata(
    name='嘴臭',
    description='最简单的嘴臭，最极致的享受',
    usage='/<curse|嘴臭|诅咒>',
    config=None
)

curse_data: list[str] = [x[1] for x in get_assets('curse')]

# message
curse = on_command('curse', aliases={'嘴臭', '诅咒'}, block=True)
@curse.handle()
async def _():
    await curse.finish(random.choice(curse_data))
