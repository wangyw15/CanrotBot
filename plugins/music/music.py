import httpx

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


async def main():
    print(await search_netease_music('another rampage'))
    print(await search_qq_music('another rampage'))

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
