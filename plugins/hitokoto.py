from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
import random

from ..data import get_data

__plugin_meta__ = PluginMetadata(
    name='一言',
    description='随机一条一言',
    usage='/<hitokoto|一言> [一言分类，默认abc]\n分类详情查看 https://developer.hitokoto.cn/sentence/#%E5%8F%A5%E5%AD%90%E7%B1%BB%E5%9E%8B-%E5%8F%82%E6%95%B0',
    config=None
)

hitokoto_data: list[dict[str, str]] = [{'content': x[1], 'from': x[2], 'from_who': x[3], 'type': x[4], 'uuid': x[5]} for x in get_data('hitokoto')]

# message
hitokoto = on_command('hitokoto', aliases={'一言'}, block=True)
@hitokoto.handle()
async def hitokoto_handle(args: Message = CommandArg()):
    """Hitokoto Handler"""
    types = ['a', 'b', 'c']
    if msg := args.extract_plain_text():
        if ' ' in msg:
            types = msg.split()
        else:
            types = list(msg)
    data = random.choice(list(filter(lambda x: x['type'] in types, hitokoto_data)))
    ret_msg = f'{data["content"]}\n-- {"" if not data["from_who"] else data["from_who"]}「{data["from"]}」\nhttps://hitokoto.cn/?uuid={data["uuid"]}'
    await hitokoto.finish(ret_msg)
