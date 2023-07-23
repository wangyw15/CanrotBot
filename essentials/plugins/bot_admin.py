from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import Event, MessageSegment
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from essentials.libraries import storage, util

__plugin_meta__ = PluginMetadata(
    name='机器人管理工具',
    description='可以在群内禁用机器人',
    usage='待定',
    config=None
)


_bot_admin_handler = on_shell_command('admin', aliases={'管理'}, block=True)
_bot_admin_data = storage.PersistentData('bot_admin')


@_bot_admin_handler.handle()
async def _(event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 1 and args[0].lower() in ['enable', '启用']:
        if gid := util.get_group_id(event):
            _bot_admin_data[gid]['enabled'] = True
            _bot_admin_data.save()
            await _bot_admin_handler.finish('已启用')
        else:
            await _bot_admin_handler.finish('仅限在群聊使用')
    elif len(args) == 1 and args[0].lower() in ['disable', '禁用']:
        if gid := util.get_group_id(event):
            _bot_admin_data[gid]['enabled'] = False
            _bot_admin_data.save()
            await _bot_admin_handler.finish('已禁用')
        else:
            await _bot_admin_handler.finish('仅限在群聊使用')
    await _bot_admin_handler.finish()


@run_preprocessor
async def _(event: Event, matcher: Matcher):
    if matcher.module.__name__ == __name__:
        return
    if gid := util.get_group_id(event):
        if gid in _bot_admin_data and 'enabled' in _bot_admin_data[gid]:
            if not _bot_admin_data[gid]['enabled']:
                await matcher.finish()
