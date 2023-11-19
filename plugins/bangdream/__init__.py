import random
from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from . import bangdream
from adapters import unified

# TODO 记得改
__plugin_meta__ = PluginMetadata(
    name='Bang Dream',
    description='邦邦功能',
    usage='还在做',
    config=None
)

_bangdream_handler = on_shell_command('bangdream', aliases={'bang', '邦邦', '邦'}, block=True)


# TODO 模拟抽卡、查卡、点歌、签到主题、活动助手等
@_bangdream_handler.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 0:
        await _bangdream_handler.finish('想要什么喵？')
    if args[0].lower() in ['comic', 'comics', '漫画', '小漫画']:
        comics = await bangdream.get_comic_list()
        if len(args) == 1:  # 随机所有小漫画
            comic_id = random.choice(list(comics.keys()))
        elif len(args) == 2 and args[1] in ['四格']:  # 随机四格
            comic_id = random.choice([i for i in comics if len(i) == 4 and i.startswith('1')])
        elif len(args) == 2 and args[1] in ['单格']:  # 随机单格
            comic_id = random.choice([i for i in comics if len(i) == 3])
        else:  # 指定漫画
            keyword = ' '.join(args[1:])
            comic_id = None
            if keyword.isdigit():
                comic_id = keyword
            else:
                for _comic_id, comic in comics.items():
                    if keyword in comic['title'].values():
                        comic_id = _comic_id
                        break
            if comic_id not in comics:
                await _bangdream_handler.finish('没有找到这个漫画喵')
        # 发送漫画
        title, _ = bangdream.get_content_by_language(comics[comic_id]['title'])
        if unified.Detector.can_send_image():
            comic_url, _ = await bangdream.get_comic_url(comic_id)
            await _bangdream_handler.finish(unified.MessageSegment(title) + unified.MessageSegment.image(comic_url))
        else:
            await _bangdream_handler.finish(f'{title}\nhttps://bestdori.com/info/comics/{comic_id}')

