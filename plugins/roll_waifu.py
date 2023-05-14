from nonebot import on_command
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
import httpx
import random

from ..libraries import user, economy, universal_adapters

__plugin_meta__ = PluginMetadata(
    name='waifu',
    description='随机 roll 老婆',
    usage='/<waifu|老婆|纸片人> [类型，默认随机]',
    config=None
)

_client = httpx.AsyncClient()
api_url = 'https://api.waifu.pics/{type}/{category}'
categories = ['waifu', 'neko', 'shinobu', 'megumin', 'bully', 'cuddle', 'cry', 'hug', 'awoo', 'kiss', 'lick', 'pat', 'smug', 'bonk', 'yeet', 'blush', 'smile', 'wave', 'highfive', 'handhold', 'nom', 'bite', 'glomp', 'slap', 'kill', 'kick', 'happy', 'wink', 'poke', 'dance', 'cringe']

async def get_waifu_url(type: str, category: str) -> str | None:
    resp = await _client.get(api_url.format(type=type, category=category))
    if resp.status_code == 200:
        return resp.json()['url']
    return None

waifu = on_command('waifu', aliases={'老婆', '纸片人'}, block=True)
@waifu.handle()
async def _(bot: Bot, event: Event, msg: Message = CommandArg()):
    if not economy.pay(user.get_uid(universal_adapters.get_puid(bot, event)), 2):
        await waifu.finish('你的余额不足哦')
    await waifu.send('谢谢你的两个胡萝卜片喵~\n正在找图哦~')
    category = random.choice(categories)
    if args := msg.extract_plain_text():
        if args == 'help' or args == '帮助':
            await waifu.finish(f'可选类型：\n{", ".join(categories)}\n或者直接 /waifu')
        elif args == 'random':
            category = random.choice(categories)
        elif args in categories:
            category = msg
        else:
            await waifu.finish('没有这个类型哦')
    img_url = await get_waifu_url('sfw', category)
    if img_url:
        await universal_adapters.send_image_from_url(img_url, bot, event)
        await waifu.finish()
    else:
        await waifu.finish('获取图片失败')
