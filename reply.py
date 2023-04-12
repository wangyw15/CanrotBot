from nonebot import get_driver, on_command, on_regex
from nonebot.adapters import Message, Event, Bot
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from pydantic import BaseModel, validator
import json
import random
import jieba

from nonebot import logger

# different bots
try:
    import nonebot.adapters.onebot.v11 as ob11
except:
    ob11 = None
try:
    import nonebot.adapters.onebot.v12 as ob12
except:
    ob12 = None
try:
    import nonebot.adapters.kaiheila as kook
except:
    kook = None
try:
    import nonebot.adapters.mirai2 as mirai2
except:
    mirai2 = None

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

# generate response
def generate_response(msg: str) -> str:
    # simai reply
    responses = []
    for _, replies in simai_data.items():
        for ask, reply in replies.items():
            if ask in msg and is_negative(ask) == is_negative(msg):
                responses += reply
    if responses:
        logger.warning(responses)
        return random.choice(responses)

    # anime_thesaurus reply
    # cut words match
    words = jieba.lcut(msg)
    for k, v in kimo_data.items():
        if k in words:
            responses += v
    # keyword match
    if not responses:
        for k, v in kimo_data.items():
            if k in msg:
                responses += v
    if responses:
        return random.choice(responses)
    
    # fallback
    return config.reply_unknown_response

async def get_user_name(event: Event, bot: Bot):
    # onebot v11
    if ob11 and isinstance(bot, ob11.Bot):
        if isinstance(event, ob11.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, ob11.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.user_id)
            return user_info['nickname']
    # onebot v12
    elif ob12 and isinstance(bot, ob12.Bot):
        if isinstance(event, ob12.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, ob12.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.user_id)
            return user_info['nickname']
    # mirai2
    elif mirai2 and isinstance(bot, mirai2.Bot):
        if isinstance(event, mirai2.GroupMessage):
            return event.sender.name
        elif isinstance(event, mirai2.FriendMessage):
            return event.sender.nickname
    # kook
    elif kook and isinstance(bot, kook.Bot):
        if isinstance(event, kook.Event):
            return event.extra.author.nikname
    return config.reply_sender_name

async def get_self_name(event: Event, bot: Bot):
    # onebot v11
    if ob11 and isinstance(bot, ob11.Bot):
        if isinstance(event, ob11.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.self_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, ob11.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.self_id)
            return user_info['nickname']
    # onebot v12
    elif ob12 and isinstance(bot, ob12.Bot):
        if isinstance(event, ob12.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.self.user_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, ob12.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.self.user_id)
            return user_info['nickname']
    # mirai2
    elif mirai2 and isinstance(bot, mirai2.Bot):
        # not implemented
        pass
    # kook
    elif kook and isinstance(bot, kook.Bot):
        if isinstance(event, kook.Event):
            return bot.self_name
    return config.reply_my_name

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
        my_name = await get_self_name(event, bot)
        user_name = await get_user_name(event, bot)
        resp = generate_response(msg).format(me=my_name, name=user_name, segment='\n')
        for i in resp.split('\n'):
            await reply.send(i)
        await reply.finish()
    await reply.finish(config.reply_unknown_response)

@auto_reply.handle()
async def _(event: Event, bot: Bot):
    """Kimo auto handler"""
    my_name = await get_self_name(event, bot)
    user_name = await get_user_name(event, bot)
    if msg := event.get_plaintext():
        resp = generate_response(msg).format(me=my_name, name=user_name)
        if resp != config.reply_unknown_response:
            for i in resp.split('\n'):
                await reply.send(i)
            await reply.finish()
