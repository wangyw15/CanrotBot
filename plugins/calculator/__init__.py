import re
import typing

from nonebot import on_regex, logger, on_command
from nonebot.adapters import Message
from nonebot.exception import FinishedException
from nonebot.params import RegexGroup, CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from . import qalculate
from .config import CalculatorConfig

__plugin_meta__ = PluginMetadata(
    name="计算器",
    description="简单的计算器",
    usage="输入表达式，以等号结尾，比如：1+1=",
    config=None,
)


def calculate(expression: str) -> str:
    if re.fullmatch(r"^([\d()\-+*/.]+)=?$", expression):
        return "{}={:g}".format(expression, eval(expression.rstrip("=")))

    if qalculate.check_qalculate():
        return qalculate.calculate(expression)

    raise NotImplementedError("未安装 qalculate，不支持此表达式: {}".format(expression))


calculator_matcher = on_regex(r"^([\d()\-+*/.]+)=$", block=True)


@calculator_matcher.handle()
async def _(
    reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()], state: T_State
):
    state["expression"] = reg[0].strip().rstrip("=")


calculator_command_handler = on_command(
    "calc", aliases={"calculator", "计算", "计算器"}, block=True
)


@calculator_command_handler.handle()
async def _(state: T_State, args: Message = CommandArg()):
    expression = args.extract_plain_text().strip()
    if not expression:
        await calculator_command_handler.finish("请输入表达式")
    state["expression"] = expression.rstrip("=")


@calculator_matcher.handle()
@calculator_command_handler.handle()
async def _(state: T_State):
    try:
        await calculator_matcher.finish(calculate(state["expression"]))
    except FinishedException:
        await calculator_matcher.finish()
    except Exception as e:
        logger.error(f"计算错误\n{str(e)}")
        await calculator_matcher.finish(f"计算错误\n{str(e)}")
