import re
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


def generate_message_from_anime_data(name: str, data: dict, possibility: float) -> str:
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
    msg = f'标题: {name if name else data["title"]}\n' \
          f'类型: {data["type"]}\n' \
          f'共 {data["episodes"]} 集\n' \
          f'状态: {anime_status}\n' \
          f'时间: {anime_time}\n' \
          f'标签: {", ".join(data["tags"])}\n' \
          f'匹配度: {possibility * 100:.2f}%'
    return msg


async def _search_anime_by_image(msg: str | MessageSegment, bot: Bot, event: Event) -> None:
    img_url = ''
    if isinstance(msg, MessageSegment) and msg.type == 'image':
        if universal_adapters.is_onebot_v11(bot) or universal_adapters.is_onebot_v12(bot):
            img_url = msg.data['url'].strip()
        elif universal_adapters.is_kook(bot):
            img_url = msg.data['file_key'].strip()
    elif isinstance(msg, universal_adapters.kook.MessageSegment) and msg.type == 'kmarkdown':
        img_url = re.search(r'\[.*]\((\S+)\)', msg.plain_text()).groups()[0]
    elif universal_adapters.is_url(msg):
        img_url = msg.strip()
    if img_url:
        search_resp = await anime.search_anime_by_image(img_url)
        if search_resp and not search_resp.get('error'):
            tracemoe_data = search_resp['result'][0]
            data = anime.search_anime_by_anilist_id(tracemoe_data['anilist'])
            ret = ''
            # 视觉图
            if universal_adapters.is_onebot_v11(bot):
                msg += f'[CQ:image,file={data["picture"]}]\n{msg}'
            elif universal_adapters.is_onebot_v12(bot):
                msg += f'[CQ:image,file={data["picture"]}]\n{msg}'
            elif universal_adapters.is_kook(bot):
                await universal_adapters.send_image(data["picture"], bot, event)
            # 生成消息
            if data:
                ret = generate_message_from_anime_data('', data, tracemoe_data["similarity"])
            # tracemoe 消息
            if universal_adapters.is_kook(bot):
                await bot.send(event, ret)
                ret = ''
            else:
                ret += f'\n{universal_adapters.MESSAGE_SPLIT_LINE}\n'
            # 视频截图
            if universal_adapters.is_onebot_v11(bot):
                msg += f'[CQ:image,file={tracemoe_data["image"]}]\n{msg}'
            elif universal_adapters.is_onebot_v12(bot):
                msg += f'[CQ:image,file={tracemoe_data["image"]}]\n{msg}'
            elif universal_adapters.is_kook(bot):
                await universal_adapters.send_image(tracemoe_data["image"], bot, event)
            # 剩下的 tracemoe 消息
            ret += f'trace.moe 信息:\n' \
                   f'番剧文件名: {tracemoe_data["filename"]}\n' \
                   f'第 {tracemoe_data["episode"]} 集\n' \
                   f'时间: {universal_adapters.seconds_to_time(tracemoe_data["from"])}~' \
                   f'{universal_adapters.seconds_to_time(tracemoe_data["to"])}\n' \
                   f'AniList 链接: https://anilist.co/anime/{tracemoe_data["anilist"]}\n'
            if universal_adapters.is_onebot_v11(bot):
                await bot.send(event, universal_adapters.ob11.Message(ret))
            elif universal_adapters.is_onebot_v12(bot):
                await bot.send(event, universal_adapters.ob12.Message(ret))
            else:
                await bot.send(event, ret)
            return
    await bot.send(event, '搜索失败')

_anime_handler = on_shell_command('anime', aliases={'动漫', '番剧'}, block=True)
@_anime_handler.handle()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 2:
        if args[0].lower() == 'search' or args[0] == '搜索':
            # 从不同的地方获取信息
            if universal_adapters.is_url(args[1]) or \
                    (isinstance(args[1], MessageSegment) and args[1].type == 'image'):
                await _search_anime_by_image(args[1], bot, event)
                await _anime_handler.finish()
            name, data, possibility = anime.search_anime_by_name(args[1])
            msg = generate_message_from_anime_data(name, data, possibility)
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
