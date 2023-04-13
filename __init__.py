from nonebot import on_command, logger
from nonebot.plugin import PluginMetadata

from . import data

__plugin_meta__ = PluginMetadata(
    name='nonebot_plugin_aio',
    description='啥都有的插件',
    usage='输入/aiohelp查看帮助',
    config=data.AIOConfig
)

if 'cp_story' not in data.aio_config.aio_disable_plugins:
    from .plugins import cp_story
    logger.info('cp_story loaded')
if 'crazy_love' not in data.aio_config.aio_disable_plugins:
    from .plugins import crazy_love
    logger.info('crazy_love loaded')
if 'curse' not in data.aio_config.aio_disable_plugins:
    from .plugins import curse
    logger.info('curse loaded')
if 'daily_news' not in data.aio_config.aio_disable_plugins:
    from .plugins import daily_news
    logger.info('daily_news loaded')
if 'hitokoto' not in data.aio_config.aio_disable_plugins:
    from .plugins import hitokoto
    logger.info('hitokoto loaded')
if 'kuji' not in data.aio_config.aio_disable_plugins:
    from .plugins import kuji
    logger.info('kuji loaded')
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