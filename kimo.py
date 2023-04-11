from nonebot import get_driver, on_command, on_regex
from nonebot.adapters import Message, Event
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from pydantic import BaseModel, validator
import json
import random
import jieba

# config
class KimoConfig(BaseModel):
    kimo_enabled: bool = True
    kimo_data: str = './anime_thesaurus.json'
    kimo_auto_rate: float = 0.0
    kimo_unknown_response: str = '我不知道怎么回答你喵~'

    @validator('kimo_enabled')
    def kimo_enabled_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('kimo_enabled must be a bool')
        return v

    @validator('kimo_data')
    def kimo_data_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('kimo_data must be a str')
        return v
    
    @validator('kimo_auto_rate')
    def kimo_auto_rate_validator(cls, v):
        if not isinstance(v, float) or v < 0 or v > 1.0:
            raise ValueError('kimo_auto_rate must be a float between 0.0 and 1.0')
        return v
    
    @validator('kimo_unknown_response')
    def kimo_unknown_response_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('kimo_unknown_response must be a str')
        return v

# metadata
__plugin_meta__ = PluginMetadata(
    name='Kimo',
    description='用Kyomotoi/AnimeThesaurus词库的自动回复（文爱）',
    usage='/文爱 对话内容',
    config=KimoConfig,
)

config = KimoConfig.parse_obj(get_driver().config)

# plugin enabled
async def is_enabled() -> bool:
    return config.kimo_enabled

# load AnimeThesaurus data
kimo_data = {}
with open(config.kimo_data, 'r', encoding='utf-8') as f:
    kimo_data = json.load(f)

# generate response
def generate_response(msg: str) -> str:
    words = jieba.lcut(msg)
    responses = []
    # cut words
    for k, v in kimo_data.items():
        if k in words:
            responses += v
    # full match
    if not responses:
        for k, v in kimo_data.items():
            if k in msg:
                responses += v
    if responses:
        return random.choice(responses)
    return config.kimo_unknown_response

# random rule
async def random_trigger() -> bool:
    return random.random() < config.kimo_auto_rate

# handler
kimo = on_command('文爱', aliases={'kimo'}, rule=is_enabled, block=True)
kimo_auto = on_regex(r'.*', rule=Rule(is_enabled, random_trigger), block=True, priority=100)

@kimo.handle()
async def kimo_handler(args: Message = CommandArg()):
    """Kimo handler"""
    if msg := args.extract_plain_text():
        await kimo.finish(generate_response(msg))
    await kimo.finish(config.kimo_unknown_response)

@kimo_auto.handle()
async def kimo_auto_handler(event: Event):
    """Kimo auto handler"""
    if msg := event.get_plaintext():
        resp = generate_response(msg)
        if resp != config.kimo_unknown_response:
            await kimo.finish(resp)
