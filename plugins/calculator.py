from nonebot import on_regex
from nonebot.typing import T_State

from ..data import add_help_message

add_help_message('任意四则运算', '简单的计算器')

calculator = on_regex(r'^([\d()\-+*/.]+)=?$', block=True)
@calculator.handle()
async def _(state: T_State):
    try:
        result = eval(state['_matched_groups'][0])
    except:
        await calculator.finish('计算错误')
    await calculator.finish(f"{state['_matched_groups'][0]}={str(result)}")
