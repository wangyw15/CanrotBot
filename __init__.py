from nonebot import on_command

from . import data
from . import daily_news
from . import hitokoto
from . import reply
from . import steam
from . import wordle
from . import yinglish
from . import cp_story

plugin_help = on_command('help', aliases={'帮助'}, block=True)

@plugin_help.handle()
async def _():
    plugin_help.finish('TODO...')
