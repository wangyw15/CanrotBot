import random
import re

import jieba
from nonebot.adapters import Event

from essentials.libraries import asset, util, storage

UNKNOWN_RESPONSE: str = '{me}不知道怎么回答{name}喵~'
AUTO_REPLY_RATE: float = 0.1  # 0~1
BOT_NAME: str = '我'
SENDER_NAME: str = '主人'

# 加载数据
_reply_data: list[dict[str, str | None]] = asset.load_json('reply.json')
_reply_group_config = storage.PersistentData('reply')


def is_negative(msg: str) -> bool:
    """
    判断是否为否定句

    :param msg: 要判断的内容

    :return: 是否为否定句
    """
    return '不' in msg


def is_single_word(msg: str) -> bool:
    """
    判断是否为单个词

    :param msg: 要判断的内容

    :return: 是否为单个词
    """
    return len(jieba.lcut(msg)) == 1


def is_regex_pattern(content: str) -> bool:
    """
    判断是否为正则表达式

    :param content: 要判断的内容

    :return: 是否为正则表达式
    """
    return content.startswith('/') and content.endswith('/') and len(content) > 2


def generate_response(msg: str, fallback_keyword: bool = True) -> str:
    """
    生成回复

    :param msg: 要回复的内容
    :param fallback_keyword: 是否使用关键词匹配回复

    :return: 回复内容
    """
    responses = []
    cut_msg = jieba.lcut(msg)

    for reply_item in _reply_data:
        pattern = reply_item['pattern']
        response = reply_item['response']
        # character = reply_item['character']
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
        return UNKNOWN_RESPONSE

    # 关键词回复
    for reply_item in _reply_data:
        pattern = reply_item['pattern']
        response = reply_item['response']
        # character = reply_item['character']
        if (not is_regex_pattern(pattern)) and pattern in msg:
            responses.append(response)
    if responses:
        return random.choice(responses)

    # 默认回复
    return UNKNOWN_RESPONSE


def get_reply_rate(group_id: str) -> float:
    """
    获取群自动回复概率

    :param group_id: 群号

    :return: 概率
    """
    if group_id in _reply_group_config:  # 存在配置
        if 'rate' in _reply_group_config[group_id]:  # 设置了概率
            return _reply_group_config[group_id]['rate']
        return AUTO_REPLY_RATE
    return 0.0


def set_reply_rate(group_id: str, rate: float) -> bool:
    """
    设置群自动回复概率

    :param group_id: 群号
    :param rate: 概率
    """
    if 0 <= rate <= 1:
        _reply_group_config[group_id]['rate'] = rate
        _reply_group_config.save()
        return True
    return False


def check_reply(event: Event) -> bool:
    """
    检查是否可以自动回复

    :param event: 事件

    :return: 是否可以自动回复
    """
    if group_id := util.get_group_id(event):  # 确保是群消息
        if group_id in _reply_group_config and _reply_group_config[group_id]['enabled']:  # 确保群开启了自动回复
            if random.random() < get_reply_rate(group_id):
                return True
    return False


def set_auto_reply_enable(group_id: str, enabled: bool):
    """
    设置群自动回复开关

    :param group_id: 群号
    :param enabled: 是否开启
    """
    if enabled and 'rate' not in _reply_group_config[group_id]:
        _reply_group_config[group_id]['rate'] = AUTO_REPLY_RATE
    _reply_group_config[group_id]['enabled'] = enabled
    _reply_group_config.save()
