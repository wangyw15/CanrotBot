from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Alconna, Image

from essentials.libraries import help, util

__plugin_meta__ = PluginMetadata(
    name="帮助", description="机器人各个插件的帮助文档", usage="/help", config=None
)

_command = on_alconna(Alconna("help"), aliases={"帮助"}, block=True)


@_command.handle()
async def _():
    if await util.can_send_segment(Image):
        _, img = await help.generate_help_image()
        await _command.finish(Image(raw=img))
    else:
        msg, _ = help.generate_help_text()
        await _command.finish(msg)
