from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment, Bot, Event
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from ..libraries import anime, universal_adapters

__plugin_meta__ = PluginMetadata(
    name='番剧工具',
    description='是个提供番剧相关的插件，但是现在只提供番剧搜索功能',
    usage='/<anime|动漫|番剧> <关键词>',
    config=None
)


_anime_handler = on_shell_command('anime', aliases={'动漫', '番剧'}, block=True)
@_anime_handler.handle()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 2:
        if args[0].lower() == 'search' or args[0] == '搜索':
            name, data, possibility = anime.search_anime(args[1])
            # 放送状态
            anime_status = '未知'
            if data["status"] == 'FINISHED':
                anime_status = '完结'
            elif data["status"] == 'ONGOING':
                anime_status = '更新中'
            elif data["status"] == 'UPCOMING':
                anime_status = '待放送'
            # 春夏秋冬季
            anime_time = f'{data["animeSeason"]["year"]}年'
            if data["animeSeason"]["season"] == 'SPRING':
                anime_time += '春季'
            elif data["animeSeason"]["season"] == 'SUMMER':
                anime_time += '夏季'
            elif data["animeSeason"]["season"] == 'FALL':
                anime_time += '秋季'
            elif data["animeSeason"]["season"] == 'WINTER':
                anime_time += '冬季'
            # 生成消息
            msg = f'名称: {name}\n' \
                  f'类型: {data["type"]}\n' \
                  f'共 {data["episodes"]} 集\n' \
                  f'状态: {anime_status}\n' \
                  f'时间: {anime_time}\n' \
                  f'标签: {", ".join(data["tags"])}\n' \
                  f'匹配度: {possibility * 100:.2f}%'
            if universal_adapters.is_onebot_v11(bot):
                msg = f'[CQ:image,file={data["picture"]}]\n{msg}'
                await _anime_handler.finish(universal_adapters.ob11.Message(msg))
            elif universal_adapters.is_onebot_v12(bot):
                msg = f'[CQ:image,file={data["picture"]}]\n{msg}'
                await _anime_handler.finish(universal_adapters.ob12.Message(msg))
            elif universal_adapters.is_kook(bot):
                await universal_adapters.send_image(data['picture'], bot, event)
                await _anime_handler.finish(msg)
            else:
                await _anime_handler.finish(msg)
