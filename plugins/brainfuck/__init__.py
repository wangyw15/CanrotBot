from arclet.alconna import Alconna, Args, Option
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    AlconnaQuery,
    Query,
)
from . import interpreter

__plugin_meta__ = PluginMetadata(
    name="Brainfuck",
    description="健脑语言",
    usage="/<bf> <代码> [输入数据]",
    config=None,
)


brainfuck_matcher = on_alconna(
    Alconna(
        "brainfuck",
        Args["code", str]["input_data", str, ""],
    ),
    aliases={"bf"},
)


@brainfuck_matcher.handle()
async def _(
    code: Query[str] = AlconnaQuery("code"),
    input_data: Query[str] = AlconnaQuery("input_data", ""),
):
    result = "运行结果为空"
    try:
        if execute_result := interpreter.execute(code.result, input_data.result):
            result = execute_result
    except Exception as e:
        result = str(e)

    await brainfuck_matcher.finish(result)
