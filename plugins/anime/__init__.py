import re
from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment, Bot, Event, Message
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from . import anime
from adapters import unified
from essentials.libraries import util


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


async def _search_anime_by_image(msg: str, bot: Bot, event: Event) -> None:
    if msg:
        search_resp = await anime.search_anime_by_image(img_url)
        if search_resp and not search_resp.get('error'):
            tracemoe_data = search_resp['result'][0]
            data = anime.search_anime_by_anilist_id(tracemoe_data['anilist'])
            final_msg = unified.Message()
            # 视觉图
            final_msg.append(unified.MessageSegment.image(data['picture'], '封面图'))
            # 生成消息
            if data:
                final_msg.append(generate_message_from_anime_data('', data, tracemoe_data["similarity"]))
            # tracemoe 消息
            # 视频截图
            final_msg.append(unified.MessageSegment.image(tracemoe_data['image'], '封面图'))
            # 剩下的 tracemoe 消息
            final_msg.append(f'trace.moe 信息:\n'
                             f'番剧文件名: {tracemoe_data["filename"]}\n'
                             f'第 {tracemoe_data["episode"]} 集\n'
                             f'时间: {util.seconds_to_time(tracemoe_data["from"])}~'
                             f'{util.seconds_to_time(tracemoe_data["to"])}\n'
                             f'AniList 链接: https://anilist.co/anime/{tracemoe_data["anilist"]}\n')
            await final_msg.send()
            return
    await bot.send(event, '搜索失败')

_anime_handler = on_shell_command('anime', aliases={'动漫', '番剧'}, block=True)
@_anime_handler.handle()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 2:
        if args[0].lower() == 'search' or args[0] == '搜索':
            # 从不同的地方获取信息
            search_keyword = await unified.adapters.get_adapter().parse_message(Message(args[1]))
            img_url = ''
            if search_keyword[0].type == unified.MessageSegmentTypes.IMAGE:
                img_url = search_keyword[0].data['file']
            elif isinstance(args[1], unified.adapters.kook_module.MessageSegment) and args[1].type == 'kmarkdown':
                img_url = re.search(r'\[.*]\((\S+)\)', args[1].plain_text()).groups()[0]
            elif util.is_url(args[1]):
                img_url = str(args[1])
            if img_url:
                await _search_anime_by_image(img_url, bot, event)
                await _anime_handler.finish()
            name, data, possibility = anime.search_anime_by_name(' '.join(args[1:]))
            text_msg = generate_message_from_anime_data(name, data, possibility)
            msg = unified.Message()
            msg.append(unified.MessageSegment.image(data['picture'], f'{name} 封面图'))
            msg.append(text_msg)
            await msg.send()
            await _anime_handler.finish()
