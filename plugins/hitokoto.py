from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
import requests
import random

from ..data import add_help_message, get_data

add_help_message('hitokoto', '/hitokoto [abcdefghijkl]')

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
