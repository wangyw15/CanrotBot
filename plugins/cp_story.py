import random
from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from ..libraries import random_text

__plugin_meta__ = PluginMetadata(
    name='CP',
    description='生成cp文',
    usage='/<cp|cp文> <攻> <受>',
    config=None
)

_cp_stories: list[dict[str, str]] = random_text.get_data('cp_story')

_cp_handler = on_shell_command('cp', aliases={'cp文'}, block=True)
@_cp_handler.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    data = random.choice(_cp_stories)
    if len(args) == 2:
        await _cp_handler.finish(data['story'].format(s=args[0], m=args[1]))
    await _cp_handler.finish(
        data['story'].format(s=data['s'] if data['s'] else '小攻', m=data['m'] if data['m'] else '小受'))
