import random
from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from ..libraries.assets import get_assets

__plugin_meta__ = PluginMetadata(
    name='CP',
    description='生成cp文',
    usage='/<cp|cp文> <攻> <受>',
    config=None
)

cp_stories: list[str] = [x[3] for x in get_assets('cp_story')]

cp = on_shell_command('cp', aliases={'cp文'}, block=True)
@cp.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 2:
        await cp.finish(random.choice(cp_stories).format(s=args[0], m=args[1]))
    await cp.finish('请输入攻和受的名字，如：/cp 攻 受')
