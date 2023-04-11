# from https://github.com/RimoChan/yinglish
from nonebot import get_driver, on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from pydantic import BaseModel, validator
import random
import jieba
import jieba.posseg as pseg

# config
class YinglishConfig(BaseModel):
    yinglish_enabled: bool = True
    yinglish_rate: float = 0.5

    @validator('yinglish_enabled')
    def yinglish_enabled_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('yinglish_enabled must be a bool')
        return v
    
    @validator('yinglish_rate')
    def yinglish_rate_validator(cls, v):
        if not isinstance(v, float) or v < 0 or v > 1.0:
            raise ValueError('yinglish_rate must be a float between 0.0 and 1.0')
        return v

# metadata
__plugin_meta__ = PluginMetadata(
    name='Yinglish',
    description='能把中文翻译成淫语的翻译机！',
    usage='/[淫语|yinglish] <内容> [淫乱度]',
    config=YinglishConfig,
)

config = YinglishConfig.parse_obj(get_driver().config)

def is_enabled() -> bool:
    return config.yinglish_enabled

# original program
jieba.setLogLevel(20)

def _词转换(x, y, 淫乱度):
    if random.random() > 淫乱度:
        return x
    if x in {'，', '。'}:
        return '……'
    if x in {'!', '！'}:
        return '❤'
    if len(x) > 1 and random.random() < 0.5:
        return f'{x[0]}……{x}'
    else:
        if y == 'n' and random.random() < 0.5:
            x = '〇' * len(x)
        return f'……{x}'

def chs2yin(s, 淫乱度=0.5):
    return ''.join([_词转换(x, y, 淫乱度) for x, y in pseg.cut(s)])

# yinglish handler
yinglish = on_command('yinglish', aliases={'淫语'}, rule=is_enabled)
@yinglish.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        splitted: list[str] = msg.split()
        if len(splitted) == 0:
            await yinglish.finish('能把中文翻译成淫语的翻译机！\n使用方法：/[淫语|yinglish] <内容> [淫乱度]')
        elif len(splitted) == 1:
            await yinglish.finish(chs2yin(msg, config.yinglish_rate))
        elif len(splitted) == 2 and splitted[1].replace('.', '').isnumeric() and 0 <= float(splitted[1]) <= 1:
            await yinglish.finish(chs2yin(splitted[0], float(splitted[1])))
        else:
            await yinglish.finish('参数错误！')
