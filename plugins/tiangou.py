from nonebot import on_command
import random

from ..data import add_help_message, get_data

add_help_message('tiangou', '随机舔狗语录')
tiangou_data: list[str] = [x[1] for x in get_data('tiangou')]

# message
tiangou = on_command('tiangou', aliases={'舔狗'}, block=True)
@tiangou.handle()
async def _():
    await tiangou.finish(random.choice(tiangou_data))
