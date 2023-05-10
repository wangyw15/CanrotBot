from nonebot import on_command, logger
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from sqlite3 import OperationalError
import nonebot

from . import data
from .universal_adapters import is_console

__plugin_meta__ = PluginMetadata(
    name='nonebot_plugin_aio',
    description='啥都有的插件',
    usage='输入/help查看帮助',
    config=data.AIOConfig
)

# import modules
data.load_plugins()

plugin_help = on_command('help', aliases={'帮助'}, block=True)
@plugin_help.handle()
async def _():
    msg = '机器人帮助：\n\n'
    for plugin in nonebot.get_loaded_plugins():
        if plugin.metadata:
            msg += f'{plugin.metadata.name}\n描述：{plugin.metadata.description}\n用法：{plugin.metadata.usage}\n--------------------\n'
    await plugin_help.finish(msg)

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
