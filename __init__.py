from nonebot import on_command, logger
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from sqlite3 import OperationalError

from . import data
from .universal_adapters import is_console

__plugin_meta__ = PluginMetadata(
    name='nonebot_plugin_aio',
    description='啥都有的插件',
    usage='输入/aiohelp查看帮助',
    config=data.AIOConfig
)

if 'calculator' not in data.aio_config.aio_disable_plugins:
    from .plugins import calculator
    logger.info('calculator loaded')
if 'cp_story' not in data.aio_config.aio_disable_plugins:
    from .plugins import cp_story
    logger.info('cp_story loaded')
if 'crazy_love' not in data.aio_config.aio_disable_plugins:
    from .plugins import crazy_love
    logger.info('crazy_love loaded')
if 'currency' not in data.aio_config.aio_disable_plugins:
    from .plugins import currency
    logger.info('currency loaded')
if 'curse' not in data.aio_config.aio_disable_plugins:
    from .plugins import curse
    logger.info('curse loaded')
if 'daily_news' not in data.aio_config.aio_disable_plugins:
    from .plugins import daily_news
    logger.info('daily_news loaded')
if 'experimental_features' not in data.aio_config.aio_disable_plugins:
    from .plugins import experimental_features
    logger.info('experimental_features loaded')
if 'hitokoto' not in data.aio_config.aio_disable_plugins:
    from .plugins import hitokoto
    logger.info('hitokoto loaded')
if 'kuji' not in data.aio_config.aio_disable_plugins:
    from .plugins import kuji
    logger.info('kuji loaded')
if 'nbnhhsh' not in data.aio_config.aio_disable_plugins:
    from .plugins import nbnhhsh
    logger.info('nbnhhsh loaded')
if 'reply' not in data.aio_config.aio_disable_plugins:
    from .plugins import reply
    logger.info('reply loaded')
if 'science_joke' not in data.aio_config.aio_disable_plugins:
    from .plugins import science_joke
    logger.info('science_joke loaded')
if 'steam' not in data.aio_config.aio_disable_plugins:
    from .plugins import steam
    logger.info('steam loaded')
if 'tiangou' not in data.aio_config.aio_disable_plugins:
    from .plugins import tiangou
    logger.info('tiangou loaded')
if 'vtb_story' not in data.aio_config.aio_disable_plugins:
    from .plugins import vtb_story
    logger.info('vtb_story loaded')
if 'wordle' not in data.aio_config.aio_disable_plugins:
    from .plugins import wordle
    logger.info('wordle loaded')
if 'yinglish' not in data.aio_config.aio_disable_plugins:
    from .plugins import yinglish
    logger.info('yinglish loaded')

plugin_help = on_command('help', aliases={'帮助'}, block=True)
@plugin_help.handle()
async def _():
    await plugin_help.finish(data.aio_help_message)

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
