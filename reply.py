from nonebot import get_driver, on_command, on_regex
from nonebot.adapters import Message, Event, Bot
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from pydantic import BaseModel, validator
import json
import random
import jieba

from .universal_adapters import *

# config
class ReplyConfig(BaseModel):
    reply_enabled: bool = True
    reply_unknown_response: str = '我不知道怎么回答你喵~'
    reply_auto_rate: float = 1.0
    reply_my_name: str = '我'
    reply_sender_name: str = '主人'

    kimo_data: str = './anime_thesaurus.json'
    simai_data: str = './simai.json'

    @validator('reply_enabled')
    def reply_enabled_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('kimo_enabled must be a bool')
        return v

    @validator('reply_unknown_response')
    def reply_unknown_response_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('reply_unknown_response must be a str')
        return v
    
    @validator('reply_auto_rate')
    def reply_auto_rate_validator(cls, v):
        if not isinstance(v, float) or v < 0 or v > 1.0:
            raise ValueError('reply_auto_rate must be a float between 0.0 and 1.0')
        return v
    
    @validator('kimo_data')
    def kimo_data_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('kimo_data must be a str')
        return v
    
    @validator('simai_data')
    def simai_data_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('simai_data must be a str')
        return v

# metadata
__plugin_meta__ = PluginMetadata(
    name='Reply',
    description='用Kyomotoi/AnimeThesaurus词库和FloatTech/zbpdata的自动回复',
    usage='/回复 对话内容',
    config=ReplyConfig,
)

config = ReplyConfig.parse_obj(get_driver().config)

# plugin enabled
async def is_enabled() -> bool:
    return config.reply_enabled

# load data
kimo_data: dict[str, list[str]] = {}
with open(config.kimo_data, 'r', encoding='utf-8') as f:
    kimo_data = json.load(f)
simai_data: dict[str, dict[str, list[str]]] = {}
with open(config.simai_data, 'r', encoding='utf-8') as f:
    simai_data = json.load(f)

def is_negative(msg: str) -> bool:
    return '不' in msg

def is_single_word(msg: str) -> bool:
    return len(jieba.lcut(msg)) == 1

# generate response
def generate_response(msg: str) -> str:
    # simai reply
    responses = []
    cut_msg = jieba.lcut(msg)
    for _, replies in simai_data.items():
        for ask, reply in replies.items():
            if ask == msg:
                responses += reply
            elif is_negative(ask) == is_negative(msg) and ask in cut_msg:
                responses += reply
            elif not is_single_word(ask) and len(cut_msg) != 0 and ask in msg:
                responses += reply
    if responses:
        return random.choice(responses)

    # anime_thesaurus reply
    # cut words match
    for k, v in kimo_data.items():
        if k in cut_msg:
            responses += v
    if responses:
        return random.choice(responses)
    
    # keyword match
    for k, v in kimo_data.items():
        if k in msg:
            responses += v
    if responses:
        return random.choice(responses)
    
    # fallback
    return config.reply_unknown_response

# random rule
def random_trigger() -> bool:
    return random.random() < config.reply_auto_rate

# handler
reply = on_command('reply', aliases={'回复', '说话', '回答我'}, rule=is_enabled, block=True)
auto_reply = on_regex(r'.*', rule=Rule(is_enabled, random_trigger), block=True, priority=100)

@reply.handle()
async def _(event: Event, bot: Bot, args: Message = CommandArg()):
    """Kimo handler"""
    if msg := args.extract_plain_text():
        my_name = await get_bot_name(event, bot, config.reply_my_name)
        user_name = await get_user_name(event, bot, config.reply_sender_name)
        resp = generate_response(msg).format(me=my_name, name=user_name, segment='\n')
        for i in resp.split('\n'):
            await reply.send(i)
        await reply.finish()
    await reply.finish(config.reply_unknown_response)

@auto_reply.handle()
async def _(event: Event, bot: Bot):
    """Kimo auto handler"""
    my_name = await get_bot_name(event, bot, config.reply_my_name)
    user_name = await get_user_name(event, bot, config.reply_sender_name)
    if msg := event.get_plaintext():
        resp = generate_response(msg).format(me=my_name, name=user_name)
        if resp != config.reply_unknown_response:
            for i in resp.split('\n'):
                await reply.send(i)
            await reply.finish()
