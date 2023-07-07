import sys
from pathlib import Path

from nonebot import on_command, load_plugins, load_plugin
from nonebot.adapters import Bot, Event
from nonebot.plugin import PluginMetadata

# 能够作为单独插件使用
sys.path.append(str(Path(__file__).parent.resolve()))

from adapters import unified
from essentials.libraries import config, help

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
    for i in plugins_path.iterdir():
        if not i.stem.startswith('_') and i.stem not in config.canrot_config.canrot_disabled_plugins:
            load_plugin(__name__ + '.plugins.' + i.stem)


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
