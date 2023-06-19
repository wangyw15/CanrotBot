from pathlib import Path
from sqlite3 import OperationalError

from nonebot import on_command, load_plugins
from nonebot.adapters import Bot, Event
from nonebot.params import CommandArg, Message
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata

from .adapters import unified
from .essentials.libraries import config, help, data

__plugin_meta__ = PluginMetadata(
    name='CanrotBot',
    description='插件本体',
    usage='输入/help查看帮助',
    config=config.CanrotConfig
)


def canrot_load_plugins() -> None:
    # 基础插件
    essentianls_plugins_path = (Path(__file__).parent / 'essentials' / 'plugins').resolve()
    load_plugins(str(essentianls_plugins_path))
    # 普通插件
    plugins_path = (Path(__file__).parent / 'plugins').resolve()
    load_plugins(str(plugins_path))


canrot_load_plugins()


plugin_help = on_command('help', aliases={'帮助'}, block=True)
@plugin_help.handle()
async def _(bot: Bot, event: Event):
    if unified.Detector.can_send_image(bot):
        _, img = await help.generate_help_message()
        await unified.MessageSegment.image(img).send(bot, event)
        await plugin_help.finish()
    else:
        msg, _ = await help.generate_help_message(False)
        await plugin_help.finish(msg)


execute_data_sql = on_command('sql_data', aliases={'sql-data', 'sqld', 'dsql', 'data-sql', 'data_sql'}, block=True)
@execute_data_sql.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if not (await SUPERUSER(bot, event) or unified.Detector.is_console(bot)):
        await execute_data_sql.finish('权限不足')
    if msg := args.extract_plain_text():
        try:
            ret = ''
            result = data.execute_sql_on_data(msg)
            for row in result:
                for col in row:
                    ret += str(col) + ' '
                ret += '\n'
            await execute_data_sql.finish(ret.strip())
        except OperationalError as e:
            await execute_data_sql.finish('SQL执行失败\n' + str(e))
        except TypeError as e:
            await execute_data_sql.finish('SQL执行失败或没有输出\n' + str(e))
    await execute_data_sql.finish('执行SQL失败')
