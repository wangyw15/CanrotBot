from datetime import timedelta

from . import util

_song_path = util.cache_path / 'song'


async def get_song_list() -> dict[str]:
    """
    获取歌曲列表

    :return: 漫画列表
    """
    return await util.bestdori_api_with_cache('songs/all.5.json', timedelta(days=7))


async def get_song_info(song_id: str) -> dict[str]:
    """
    获取歌曲信息

    :param song_id: 歌曲ID

    :return: 歌曲信息
    """
    return await util.bestdori_api_with_cache(f'songs/{song_id}.json')


async def get_song_url(song_id: str) -> str | None:
    """
    获取歌曲音频链接

    :param song_id: 歌曲ID

    :return: 歌曲音频链接
    """
    songs = await get_song_list()
    if song_id not in songs:
        return None
    song_id = song_id.zfill(3)
    return f'https://bestdori.com/assets/jp/sound/bgm{song_id}_rip/bgm{song_id}.mp3'
