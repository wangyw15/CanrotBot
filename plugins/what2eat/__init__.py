import typing

from nonebot import on_regex
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata

from . import what2eat

__plugin_meta__ = PluginMetadata(
    name='今天吃/喝吃什么',
    description='选择恐惧症？让坎洛特建议你今天吃/喝什么！',
    usage='还没做完',
    config=None
)


_brand_handler = on_regex(r'我(?:想|要)(吃|喝)(\S+)', block=True)


@_brand_handler.handle()
async def _(reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]):
    if reg[0] == '喝':
        await _brand_handler.finish(f'可以试试 {what2eat.get_drink_by_brand(reg[1])}')
    await _brand_handler.finish()
