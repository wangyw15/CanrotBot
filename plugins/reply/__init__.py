from nonebot import on_command, on_regex
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

import essentials.libraries.user
from essentials.libraries import util

from . import reply

__plugin_meta__ = PluginMetadata(
    name="自动回复",
    description="自动回复，附赠自动水群功能",
    usage=f"/<reply|回复|说话|回答我> <要说的话>，或者也有几率触发机器人自动回复",
)

# TODO 利用 LLM 实现
