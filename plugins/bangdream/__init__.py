import difflib
import random

from arclet.alconna import Option, Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Alconna, AlconnaQuery, Query, UniMsg, Text, Image, Voice

from essentials.libraries import util
from . import bestdori

# TODO 记得改；模拟抽卡、查卡、点歌、签到主题、活动助手等
__plugin_meta__ = PluginMetadata(
    name='Bang Dream',
    description='邦邦功能',
    usage='还在做',
    config=None
)

_command = on_alconna(Alconna(
    '邦邦',
    Option(
        'comic',
        Args['comic_query', str, 'random'],
        alias=['漫画', '小漫画', '四格', '单格'],
        help_text='随机小漫画'
    ),
    Option(
        'song',
        Args['song_query', str, 'random'],
        alias=['歌曲', '查歌', '查曲'],
        help_text='查游戏内歌曲'
    ),
), aliases={'bangdream'}, block=True)


@_command.assign('comic')
async def _(comic_query: Query[str] = AlconnaQuery('comic_query', 'random')):
    comic_query = comic_query.result.strip()
    comics = await bestdori.comic.get_comic_list()
    comic_id = None
    if comic_query == 'random':
        comic_id = random.choice(list(comics.keys()))
    elif comic_query == '单格':
        comic_id = random.choice([i for i in comics if len(i) == 3])
    elif comic_query == '四格':
        comic_id = random.choice([i for i in comics if len(i) == 4 and i.startswith('1')])
    elif comic_query.isdigit() and comic_query in comics:
        comic_id = comic_query
    else:
        best_match = 0.0
        for _comic_id, comic in comics.items():
            for _title in comic['title']:
                ratio = difflib.SequenceMatcher(None, comic_query, str(_title)).quick_ratio()
                if ratio > best_match:
                    best_match = ratio
                    comic_id = _comic_id
    if comic_id is None or comic_id not in comics:
        await _command.finish('没有找到这个漫画喵')
    title, _ = bestdori.util.get_content_by_language(comics[comic_id]['title'])
    msg = UniMsg()
    msg.append(Text(title))
    if await util.can_send_segment(Image):
        result = await bestdori.comic.get_comic(comic_id)
        msg.append(Image(raw=result[0]))
    else:
        msg.append(Text(f'\nhttps://bestdori.com/info/comics/{comic_id}'))
    await _command.finish(msg)


@_command.assign('song')
async def _(song_query: Query[str] = AlconnaQuery('song_query', 'random')):
    song_query = song_query.result.strip()
    songs = await bestdori.song.get_song_list()
    song_id = None
    if song_query == 'random':
        song_id = random.choice(list(songs.keys()))
    elif song_query.isdigit() and song_query in songs:
        song_id = song_query
    else:
        best_match = 0.0
        for _song_id, song in songs.items():
            for _title in song['musicTitle']:
                ratio = difflib.SequenceMatcher(None, song_query, str(_title)).quick_ratio()
                if ratio > best_match:
                    best_match = ratio
                    song_id = _song_id
    if song_id is None or song_id not in songs:
        await _command.finish('没有找到这首歌喵')
    info = await bestdori.song.get_song_info(song_id)
    # TODO 封面（难做
    await _command.send(f'{bestdori.util.get_content_by_language(info["musicTitle"])[0]}\n'
                        f'作词：{bestdori.util.get_content_by_language(info["lyricist"])[0]}\n'
                        f'作曲：{bestdori.util.get_content_by_language(info["composer"])[0]}\n'
                        f'编曲：{bestdori.util.get_content_by_language(info["arranger"])[0]}\n'
                        f'链接：https://bestdori.com/info/songs/{song_id}')
    # 发送信息
    if await util.can_send_segment(Voice):
        await _command.send(Voice(url=await bestdori.song.get_song_url(song_id)))
    await _command.finish()


@_command.handle()
async def _():
    await _command.finish(Text('用法：' + __plugin_meta__.usage))
