from nonebot import get_driver, on_command, on_regex
from nonebot.adapters import Message, Event, Bot
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from pydantic import BaseModel, validator
import random
import jieba
import re

from .universal_adapters import *
from .data import get_data

# config
class ReplyConfig(BaseModel):
    reply_enabled: bool = True
    reply_unknown_response: str = '我不知道怎么回答你喵~'
    reply_auto_rate: float = 1.0
    reply_my_name: str = '我'
    reply_sender_name: str = '主人'

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
reply_data: list[dict[str, str | None]] = [{ 'pattern': x[1], 'response': x[2], 'character': x[3] } for x in get_data('reply')]

def is_negative(msg: str) -> bool:
    return '不' in msg

def is_single_word(msg: str) -> bool:
    return len(jieba.lcut(msg)) == 1

# generate response
def generate_response(msg: str) -> str:
    responses = []
    cut_msg = jieba.lcut(msg)

    for reply_item in reply_data:
        pattern = reply_item['pattern']
        response = reply_item['response']
        character = reply_item['character']
        if pattern == msg:
            responses.append(response)
        elif is_negative(pattern) == is_negative(msg) and pattern in cut_msg:
            responses.append(response)
        elif not is_single_word(pattern) and len(cut_msg) != 0 and pattern in msg:
            responses.append(response)
    if responses:
        return random.choice(responses)

    # keyword match
    for reply_item in reply_data:
        pattern = reply_item['pattern']
        response = reply_item['response']
        character = reply_item['character']
        if pattern in msg:
            responses.append(response)
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
