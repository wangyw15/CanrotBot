from nonebot import on_command
import random

from ..data import add_help_message, get_data

add_help_message('vtb_story', 'vTuber小作文')
vtb_story_data: list[str] = [x[1] for x in get_data('vtb_story')]

# message
vtb_story = on_command('vtb-story', aliases={'vtb_story', 'vtb小作文'}, block=True)
@vtb_story.handle()
async def _():
    await vtb_story.finish(random.choice(vtb_story_data))
