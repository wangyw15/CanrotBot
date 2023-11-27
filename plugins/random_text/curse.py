import random

from nonebot import on_command
from nonebot.plugin import PluginMetadata

from . import get_data

__plugin_meta__ = PluginMetadata(
    name="骂我",
    description="最简单的嘴臭，最极致的享受（抖M模拟器）",
    usage="/<curse|嘴臭|诅咒|骂我>",
    config=None,
)

_curse_data: list[dict[str, str]] = get_data("curse")
_curse_handler = on_command("curse", aliases={"嘴臭", "诅咒", "骂我"}, block=True)


@_curse_handler.handle()
async def _():
    await _curse_handler.finish(random.choice(_curse_data)["content"])
