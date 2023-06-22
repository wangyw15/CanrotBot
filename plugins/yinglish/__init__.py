from typing import Annotated

from nonebot import get_driver, on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata
from pydantic import BaseModel

from . import yinglish

__plugin_meta__ = PluginMetadata(
    name='yinglish',
    description='能把中文翻译成淫语的翻译机！',
    usage='/<淫语|yinglish> <内容> [淫乱度(0-1之间的小数)]',
    config=None
)

# config
class YinglishConfig(BaseModel):
    yinglish_rate: float = 1.0


_config = YinglishConfig.parse_obj(get_driver().config)


# yinglish handler
_yinglish_handler = on_shell_command('yinglish', aliases={'淫语'}, block=True)
@_yinglish_handler.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 0:
        await _yinglish_handler.finish('能把中文翻译成淫语的翻译机！\n使用方法：' + __plugin_meta__.usage)
    elif len(args) == 1:
        await _yinglish_handler.finish(yinglish.chs2yin(args[0], _config.yinglish_rate))
    elif len(args) == 2 and args[1].replace('.', '').isnumeric() and 0 <= float(args[1]) <= 1:
        await _yinglish_handler.finish(yinglish.chs2yin(args[0], float(args[1])))
    else:
        await _yinglish_handler.finish('参数错误！\n使用方法：' + __plugin_meta__.usage)
