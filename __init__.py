from nonebot import on_command, logger
from nonebot.plugin import PluginMetadata

from . import data

__plugin_meta__ = PluginMetadata(
    name='nonebot_plugin_aio',
    description='啥都有的插件',
    usage='输入/aiohelp查看帮助',
    config=data.AIOConfig
)

if 'daily_news' not in data.aio_config.aio_disable_plugins:
    from .plugins import daily_news
    logger.info('daily_news loaded')
if 'hitokoto' not in data.aio_config.aio_disable_plugins:
    from .plugins import hitokoto
    logger.info('hitokoto loaded')
if 'reply' not in data.aio_config.aio_disable_plugins:
    from .plugins import reply
    logger.info('reply loaded')
if 'steam' not in data.aio_config.aio_disable_plugins:
    from .plugins import steam
    logger.info('steam loaded')
if 'wordle' not in data.aio_config.aio_disable_plugins:
    from .plugins import wordle
    logger.info('wordle loaded')
if 'yinglish' not in data.aio_config.aio_disable_plugins:
    from .plugins import yinglish
    logger.info('yinglish loaded')
if 'cp_story' not in data.aio_config.aio_disable_plugins:
    from .plugins import cp_story
    logger.info('cp_story loaded')

plugin_help = on_command('help', aliases={'帮助'}, block=True)

@plugin_help.handle()
async def _():
    await plugin_help.finish(data.aio_help_message)
