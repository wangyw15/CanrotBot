from nonebot import on_command
from nonebot.plugin import PluginMetadata
import random

from ..data import get_data

__plugin_meta__ = PluginMetadata(
    name='vtb小作文',
    description='管人痴（',
    usage='/<vtb-story|vtb_story|vtb小作文>',
    config=None
)

vtb_story_data: list[str] = [x[1] for x in get_data('vtb_story')]

# message
vtb_story = on_command('vtb-story', aliases={'vtb_story', 'vtb小作文'}, block=True)
@vtb_story.handle()
async def _():
    await vtb_story.finish(random.choice(vtb_story_data))
