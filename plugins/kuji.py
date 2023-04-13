from nonebot import on_command
import random

from ..data import add_help_message, get_data

add_help_message('kuji', '赛博浅草寺')
kuji_data: list[str] = [x[1] for x in get_data('kuji')]

# message
kuji = on_command('kuji', aliases={'浅草寺'}, block=True)
@kuji.handle()
async def _():
    await kuji.finish(random.choice(kuji_data))
