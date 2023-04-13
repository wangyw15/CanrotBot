from nonebot import on_command
import random

from ..data import add_help_message, get_data

add_help_message('crazy-love', '发癫文')
crazy_love_data: list[str] = [x[1] for x in get_data('crazy_love')]

# message
crazy_love = on_command('crazy-love', aliases={'发癫', '发电', 'crazy_love'}, block=True)
@crazy_love.handle()
async def _():
    await crazy_love.finish(random.choice(crazy_love_data))
