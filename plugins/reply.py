import random
import re

import jieba
from nonebot import get_driver, on_command, on_regex
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from pydantic import BaseModel

import essentials.libraries.user
from essentials.libraries import asset, util, storage


# config
class ReplyConfig(BaseModel):
    reply_unknown_response: str = '我不知道怎么回答你喵~'
    reply_auto_rate: float = 1.0  # 0~1
    reply_my_name: str = '我'
    reply_sender_name: str = '主人'


config = ReplyConfig.parse_obj(get_driver().config)

__plugin_meta__ = PluginMetadata(
    name='自动回复',
    description='自动回复，附赠自动水群功能',
    usage=f'/<reply|回复|说话|回答我> <要说的话>，或者也有{config.reply_auto_rate * 100}%的几率触发机器人自动回复',
    config=ReplyConfig
)

# 加载数据
_reply_data: list[dict[str, str | None]] = asset.load_json('reply.json')
_reply_group_config = storage.PersistentData('reply')


def is_negative(msg: str) -> bool:
    return '不' in msg


def is_single_word(msg: str) -> bool:
    return len(jieba.lcut(msg)) == 1


def is_regex_pattern(content: str) -> bool:
    return content.startswith('/') and content.endswith('/') and len(content) > 2


# generate response
def generate_response(msg: str, fallback_keyword: bool = True) -> str:
    responses = []
    cut_msg = jieba.lcut(msg)

    for reply_item in _reply_data:
        pattern = reply_item['pattern']
        response = reply_item['response']
        character = reply_item['character']
        if is_regex_pattern(pattern):
            pattern = pattern[1:-1]
            if re.search(pattern, msg):
                responses.append(response)
        elif pattern == msg:
            responses.append(response)
        elif is_negative(pattern) == is_negative(msg) and pattern in cut_msg:
            responses.append(response)
        elif not is_single_word(pattern) and len(cut_msg) != 0 and pattern in msg:
            responses.append(response)
    if responses:
        return random.choice(responses)

    if not fallback_keyword:
        return config.reply_unknown_response

    # keyword match
    for reply_item in _reply_data:
        pattern = reply_item['pattern']
        response = reply_item['response']
        character = reply_item['character']
        if (not is_regex_pattern(pattern)) and pattern in msg:
            responses.append(response)
    if responses:
        return random.choice(responses)
    
    # fallback
    return config.reply_unknown_response


reply = on_command('reply', aliases={'回复', '说话', '回答我'}, block=True)
auto_reply = on_regex(r'.*', block=True, priority=100)  # TODO 不同群不同概率


@reply.handle()
async def _(event: Event, bot: Bot, args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        if msg.startswith('_'):
            gid = util.get_group_id(event)
            if msg.lower() == '_enable':
                _reply_group_config[gid]['enabled'] = True
                _reply_group_config.save()
                await reply.finish('已启用自动回复')
            elif msg.lower() == '_disable':
                _reply_group_config[gid]['enabled'] = False
                _reply_group_config.save()
                await reply.finish('已禁用自动回复')
            elif msg.lower().startswith('_rate'):
                rate = float(msg.split()[1])
                if 0 <= rate <= 1:
                    _reply_group_config[gid]['rate'] = rate
                    _reply_group_config.save()
                    await reply.finish(f'已将自动回复概率设置为{rate * 100}%')
                else:
                    await reply.finish('概率必须在0~1之间')
        my_name = await util.get_bot_name(event, bot, config.reply_my_name)
        user_name = await essentials.libraries.user.get_user_name(event, bot, config.reply_sender_name)
        resp = generate_response(msg).format(me=my_name, name=user_name, segment='\n')
        for i in resp.split('\n'):
            await reply.send(i)
        await reply.finish()
    await reply.finish(config.reply_unknown_response)


@auto_reply.handle()
async def _(event: Event, bot: Bot):
    if group_id := util.get_group_id(event):  # 确保是群消息
        if group_id in _reply_group_config and _reply_group_config[group_id]['enabled']:  # 确保群开启了自动回复
            rate = config.reply_auto_rate
            if 'rate' in _reply_group_config[group_id]:
                rate = _reply_group_config[group_id]['rate']
            if random.random() < rate: # 概率
                my_name = await util.get_bot_name(event, bot, config.reply_my_name)
                user_name = await essentials.libraries.user.get_user_name(event, bot, config.reply_sender_name)
                if msg := event.get_plaintext():
                    resp = generate_response(msg, False).format(me=my_name, name=user_name)
                    if resp != config.reply_unknown_response:
                        for i in resp.split('\n'):
                            await reply.send(i)
    await reply.finish()
