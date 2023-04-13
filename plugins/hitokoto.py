from nonebot import on_command
import requests

from ..data import add_help_message

add_help_message('hitokoto', '一言')

# message
hitokoto = on_command('hitokoto', aliases={'一言'}, block=True)

def fetch_hitokoto():
    """Fetch Hitokoto"""
    r = requests.get('https://v1.hitokoto.cn/?c=a&c=b&c=c')
    data = r.json()
    return f'{data["hitokoto"]}\n-- {"" if not data["from_who"] else data["from_who"]}「{data["from"]}」\nhttps://hitokoto.cn/?uuid={data["uuid"]}'

@hitokoto.handle()
async def hitokoto_handle():
    """Hitokoto Handler"""
    await hitokoto.finish(fetch_hitokoto())
