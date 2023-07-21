from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from adapters import unified
from essentials.libraries import util

__plugin_meta__ = PluginMetadata(
    name='Pixiv助手',
    description='提供一些有关 Pixiv 的功能',
    usage='发id看图，没了',
    config=None
)


_pixiv_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51',
    'Referer': 'https://www.pixiv.net/'
}


_pixiv_handler = on_shell_command('pixiv', aliases={'Pixiv', '蓝p', '蓝P'})


@_pixiv_handler.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 1 and args[0].isdigit():
        data = await util.fetch_json_data(f'https://px2.rainchan.win/json/{args[0]}')
        if data:
            if not data['error']:
                imgurl = data['body'][0]['urls']['original']
                imgdata = await util.fetch_bytes_data(imgurl, headers=_pixiv_headers)
                if imgdata:
                    await unified.MessageSegment.image(imgdata).send()
                    await _pixiv_handler.finish()
                else:
                    await _pixiv_handler.finish('图片下载失败')
            else:
                await _pixiv_handler.finish(data['message'])
        else:
            await _pixiv_handler.finish('图片查找失败')
