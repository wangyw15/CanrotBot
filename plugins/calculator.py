import typing

from nonebot import on_regex
from nonebot.exception import FinishedException
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='计算器',
    description='简单的计算器',
    usage='输入表达式，以等号结尾，比如：1+1=',
    config=None
)


calculator = on_regex(r'^([\d()\-+*/.]+)[=＝]$', block=True)


@calculator.handle()
async def _(reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]):
    try:
        result = eval(reg[0].strip())
        await calculator.finish(f'{reg[0]}={str(result)}')
    except FinishedException:
        pass
    except:
        await calculator.finish('计算错误')
