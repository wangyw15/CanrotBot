from nonebot import on_command, logger
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from sqlite3 import OperationalError
import nonebot

from . import data
from .universal_adapters import *

__plugin_meta__ = PluginMetadata(
    name='nonebot_plugin_aio',
    description='啥都有的插件',
    usage='输入/help查看帮助',
    config=data.CanrotConfig
)

# import modules
data.load_plugins()

plugin_help = on_command('help', aliases={'帮助'}, block=True)
@plugin_help.handle()
async def _(bot: Bot, event: Event):
    msg = ''
    for plugin in nonebot.get_loaded_plugins():
        if plugin.metadata:
            msg += f'{plugin.metadata.name}\n描述：{plugin.metadata.description}\n用法：{plugin.metadata.usage}\n{MESSAGE_SPLIT_LINE}\n'
    if is_onebot_v11(bot) or is_onebot_v12(bot):
        splitted_msg: list[str] = [x.strip() for x in msg.split(MESSAGE_SPLIT_LINE) if x]
        msg_nodes = generate_onebot_group_forward_message(splitted_msg, await get_bot_name(event, bot, 'Canrot'), bot.self_id)
        if isinstance(event, ob11.GroupMessageEvent) or isinstance(event, ob12.GroupMessageEvent):
            await bot.send_group_forward_msg(group_id=event.group_id, messages=msg_nodes)
        elif isinstance(event, ob11.PrivateMessageEvent) or isinstance(event, ob12.PrivateMessageEvent):
            await bot.send_group_forward_msg(user_id=event.user_id, messages=msg_nodes)
        await plugin_help.finish()
    await plugin_help.finish('机器人帮助：\n\n' + msg)

execute_sql = on_command('sql', aliases={'SQL'}, block=True)
@execute_sql.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if not (await SUPERUSER(bot, event) or is_console(bot)):
        await execute_sql.finish('权限不足')
    if msg := args.extract_plain_text():
        try:
            ret = ''
            result = data.execute_sql(msg)
            for row in result:
                for col in row:
                    ret += str(col) + ' '
                ret += '\n'
            await execute_sql.finish(ret)
        except OperationalError as e:
            await execute_sql.finish('SQL查询失败\n' + str(e))
    await execute_sql.finish('执行SQL失败')
