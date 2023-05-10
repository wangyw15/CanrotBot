from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
import random

from ..data import get_data

__plugin_meta__ = PluginMetadata(
    name='CP',
    description='生成cp文',
    usage='/<cp|cp文> <攻> <受>',
    config=None
)

cp_stories: list[str] = [x[3] for x in get_data('cp_story')]

cp = on_command('cp', aliases={'cp文'}, block=True)
@cp.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        if ' ' in msg:
            splitted = msg.split()
            await cp.finish(random.choice(cp_stories).format(s=splitted[0], m=splitted[1]))
    await cp.finish('请输入攻和受的名字，如：/cp 攻 受')
