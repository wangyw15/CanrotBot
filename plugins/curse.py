from nonebot import on_command
import random

from ..data import add_help_message, get_data

add_help_message('curse', '嘴臭语录')
curse_data: list[str] = [x[1] for x in get_data('curse')]

# message
curse = on_command('curse', aliases={'嘴臭', '诅咒'},block=True)
@curse.handle()
async def _():
    await curse.finish(random.choice(curse_data))
