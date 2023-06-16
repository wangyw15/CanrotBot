from nonebot import on_command
from nonebot.plugin import PluginMetadata
import random

from ..libraries import random_text

__plugin_meta__ = PluginMetadata(
    name='嘴臭',
    description='最简单的嘴臭，最极致的享受',
    usage='/<curse|嘴臭|诅咒>',
    config=None
)

_curse_data: list[dict[str, str]] = random_text.get_data('curse')

# message
_curse_handler = on_command('curse', aliases={'嘴臭', '诅咒'}, block=True)
@_curse_handler.handle()
async def _():
    await _curse_handler.finish(random.choice(_curse_data)['content'])
