from typing import Annotated
from urllib import parse

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from . import idolypride

__plugin_meta__ = PluginMetadata(
    name='IDOLY PRIDE',
    description='只做了日历',
    usage='/<ip|偶像荣耀|idolypride> <功能>',
    config=None
)


_ip_handler = on_shell_command('idolypride', aliases={'ip', '偶像荣耀'}, block=True)
@_ip_handler.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if args:
        if args[0] in ['events', 'calendar', '活动', '日历']:
            data = await idolypride.get_today_events()
            if data:
                msg = ''
                for i in data:
                    msg += f'{i["name"]}\n' \
                           f'开始时间: {i["start"].strftime("%Y-%m-%d")}\n' \
                           f'结束时间: {i["end"].strftime("%Y-%m-%d")}\n' \
                           f'类型: {i["type"]}\n'
                    msg += f'链接: https://wiki.biligame.com/idolypride/{parse.quote(i["page"])}\n' if i["page"] else ''
                    msg += '\n'
                await _ip_handler.finish(msg.strip())
            else:
                await _ip_handler.finish('今天没有活动喵~')
    await _ip_handler.finish(__plugin_meta__.usage)
