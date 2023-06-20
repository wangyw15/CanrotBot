from typing import Annotated

import httpx
from nonebot import on_shell_command
from nonebot.adapters import Bot, Event, MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from adapters import unified

__plugin_meta__ = PluginMetadata(
    name='Pixiv助手',
    description='提供一些有关 Pixiv 的功能',
    usage='发id看图，没了',
    config=None
)


if proxy := unified.util._get_config('canrot_proxy'):
    _client = httpx.AsyncClient(proxies=proxy)
else:
    _client = httpx.AsyncClient()
_client.timeout = 10


_pixiv_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
    'Referer': 'https://www.pixiv.net/'
}


_pixiv_handler = on_shell_command('pixiv', aliases={'Pixiv', '蓝p', '蓝P'})
@_pixiv_handler()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 1 and args[0].isdigit():
        resp = await _client.get(f'https://px2.rainchan.win/json/{args[0]}')
        if resp.is_success and resp.status_code == 200:
            data = resp.json()
            if not data['error']:
                imgurl = data['body']['urls']['original']
                imgresp = await _client.get(imgurl, headers=_pixiv_headers)
                if imgresp.is_success and imgresp.status_code == 200:
                    await unified.MessageSegment.image(imgresp.content).send(bot, event)
                    await _pixiv_handler.finish()
                else:
                    await _pixiv_handler.finish('图片下载失败')
            else:
                await _pixiv_handler.finish(data['message'])
        await _pixiv_handler.finish('图片查找失败')
