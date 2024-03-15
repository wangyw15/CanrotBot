import typing

from nonebot import on_regex
from nonebot.exception import FinishedException
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="计算器",
    description="简单的计算器",
    usage="输入表达式，以等号结尾，比如：1+1=",
    config=None,
)


calculator_matcher = on_regex(r"^([\d()\-+*/.]+)[=＝]$", block=True)


@calculator_matcher.handle()
async def _(reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]):
    try:
        result = eval(reg[0].strip())
        await calculator_matcher.finish("{}={:g}".format(reg[0], result))
    except FinishedException:
        await calculator_matcher.finish()
    except Exception as e:
        await calculator_matcher.finish(f"计算错误\n{str(e)}")
