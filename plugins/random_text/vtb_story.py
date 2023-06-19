from nonebot import on_command
from nonebot.plugin import PluginMetadata
import random

from . import get_data

__plugin_meta__ = PluginMetadata(
    name='vtb小作文',
    description='管人痴（',
    usage='/<vtb-story|vtb_story|vtb小作文>',
    config=None
)

_vtb_story_data: list[str] = get_data('vtb_story')

# message
_vtb_story_handler = on_command('vtb-story', aliases={'vtb_story', 'vtb小作文'}, block=True)
@_vtb_story_handler.handle()
async def _():
    await _vtb_story_handler.finish(random.choice(_vtb_story_data))
