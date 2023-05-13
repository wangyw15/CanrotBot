from nonebot import on_command, load_plugins
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from sqlite3 import OperationalError
from pathlib import Path
import nonebot

from .libraries import config, assets
from .libraries.universal_adapters import *

__plugin_meta__ = PluginMetadata(
    name='CanrotBot',
    description='插件本体',
    usage='输入/help查看帮助',
    config=config.CanrotConfig
)

def canrot_load_plugins() -> None:
    plugins_path = Path(__file__).parent.joinpath('plugins').resolve()
    load_plugins(plugins_path)

canrot_load_plugins()

plugin_help = on_command('help', aliases={'帮助'}, block=True)
@plugin_help.handle()
async def _(bot: Bot, event: Event):
    splitted_msg: list[str] = []
    for plugin in nonebot.get_loaded_plugins():
        if plugin.metadata:
            splitted_msg.append(f'{plugin.metadata.name}\n描述：{plugin.metadata.description}\n用法：{plugin.metadata.usage}')
    await send_group_forward_message(splitted_msg, bot, event, header='机器人帮助：')
    await plugin_help.finish()

execute_sql = on_command('sql', aliases={'SQL'}, block=True)
@execute_sql.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if not (await SUPERUSER(bot, event) or is_console(bot)):
        await execute_sql.finish('权限不足')
    if msg := args.extract_plain_text():
        try:
            ret = ''
            result = assets.execute_sql_on_assets(msg)
            for row in result:
                for col in row:
                    ret += str(col) + ' '
                ret += '\n'
            await execute_sql.finish(ret)
        except OperationalError as e:
            await execute_sql.finish('SQL查询失败\n' + str(e))
    await execute_sql.finish('执行SQL失败')
