from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Alconna, Image

from essentials.libraries import help, util

__plugin_meta__ = PluginMetadata(
    name="Help", description="帮助手册", usage="/help", config=None
)

_command = on_alconna(Alconna("help"), aliases={"帮助"}, block=True)


@_command.handle()
async def _():
    if await util.can_send_segment(Image):
        _, img = await help.generate_help_message()
        await _command.finish(Image(raw=img))
    else:
        msg, _ = await help.generate_help_message(False)
        await _command.finish(msg)
