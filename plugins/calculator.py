from nonebot import on_regex
from nonebot.exception import FinishedException
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='计算器',
    description='简单的计算器',
    usage='输入表达式，以等号结尾，比如：1+1=',
    config=None
)

calculator = on_regex(r'^([\d()\-+*/.]+)[=＝]$', block=True)
@calculator.handle()
async def _(state: T_State):
    try:
        result = eval(state['_matched_groups'][0].strip())
        await calculator.finish(f"{state['_matched_groups'][0]}={str(result)}")
    except FinishedException:
        pass
    except:
        await calculator.finish('计算错误')
