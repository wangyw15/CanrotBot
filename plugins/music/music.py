import typing

import httpx
import nonebot.adapters.mirai2 as mirai2
import nonebot.adapters.onebot.v11 as ob11
import nonebot.adapters.onebot.v12 as ob12
from nonebot.adapters import Bot

_client = httpx.AsyncClient()


async def resolve_shortlink(url: str) -> str:
    resp = await _client.get(url, follow_redirects=False)
    if resp.status_code == 302:
        return resp.headers['Location']
    return ''


async def search_netease_music(keyword: str) -> list[dict]:
    resp = await _client.get('https://music.163.com/api/search/get/web', params={'s': keyword, 'type': 1})
    if resp.is_success and resp.status_code == 200:
        data = resp.json()
        if data['code'] == 200:
            return data['result']['songs']
    return []


async def search_qq_music(keyword: str) -> list[dict]:
    resp = await _client.get('https://c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg',
                             params={'key': keyword, 'format': 'json', 'inCharset': 'utf-8', 'outCharset': 'utf-8'})
    if resp.is_success and resp.status_code == 200:
        data = resp.json()
        if data['code'] == 0:
            return data['data']['song']['itemlist']
    return []


async def fetch_music_info(music_type: typing.Literal['qq', '163'], music_id: str | int) -> dict:
    ret = {}
    if music_type == '163':
        resp = await _client.get(f'https://autumnfish.cn/song/detail?ids={music_id}')
        if resp.is_success and resp.status_code == 200:
            data = resp.json()['songs'][0]
            ret['title'] = data['name']
            ret['artists'] = '/'.join([artist['name'] for artist in data['ar']])
            ret['cover'] = data['al']['picUrl']
    elif music_type == 'qq':
        pass
    return ret


async def is_qq(bot: Bot) -> bool:
    return isinstance(bot, ob11.Bot) or isinstance(bot, ob12.Bot) or isinstance(bot, mirai2.Bot)


async def main():
    print(await search_netease_music('another rampage'))
    print(await search_qq_music('another rampage'))

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
