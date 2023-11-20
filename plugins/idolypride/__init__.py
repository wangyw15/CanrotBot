from urllib import parse

from arclet.alconna import Alconna
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Option

from . import idolypride

__plugin_meta__ = PluginMetadata(
    name='IDOLY PRIDE',
    description='只做了日历',
    usage='/<ip|偶像荣耀|idolypride> <功能>',
    config=None
)


_command = on_alconna(Alconna(
    '偶像荣耀',
    Option(
        'events',
        alias=['calendar', '活动', '日历'],
    )
), block=True)


@_command.assign('events')
async def _():
    data = await idolypride.get_today_events()
    if data:
        msg = '偶像荣耀现在的活动: \n\n'
        for i in data:
            msg += f'{i["name"]}\n' \
                   f'开始时间: {i["start"].strftime("%Y-%m-%d")}\n' \
                   f'结束时间: {i["end"].strftime("%Y-%m-%d")}\n' \
                   f'类型: {i["type"]}\n'
            msg += f'链接: https://wiki.biligame.com/idolypride/{parse.quote(i["page"])}\n' if i["page"] else ''
            msg += '\n'
        await _command.finish(msg.strip())
    else:
        await _command.finish('今天没有活动喵~')


@_command.handle()
async def _():
    await _command.finish(__plugin_meta__.usage)
