import asyncio
import re
from typing import Literal

import httpx
from bs4 import BeautifulSoup

from .render_by_browser import get_new_page

_client: httpx.AsyncClient | None = None


def init_web_client(proxy: str = None) -> None:
    global _client
    if proxy:
        _client = httpx.AsyncClient(proxies=proxy)
    else:
        _client = httpx.AsyncClient()
    _client.timeout = 10


async def search_muse_dash_player_id(player_name: str) -> str | None:
    if not _client:
        return None
    resp = await _client.get(f'https://api.musedash.moe/search/{player_name}')
    if resp.status_code == 200:
        data: list[list[str]] = resp.json()
        if data and len(data) != 0 and data[0][0] == player_name:
            return data[0][1]
    return None


async def fetch_muse_dash_player_data(player_id: str) -> dict | None:
    if not _client:
        return None
    resp = await _client.get(f'https://musedash.moe/player/{player_id}?lang=ChineseS')
    if resp.status_code == 200:
        return _parse_muse_dash_page(resp.text)
    return None


def _parse_muse_dash_page(content: str) -> dict:
    soup = BeautifulSoup(content, 'html.parser')
    result = {}
    # player name and diff
    name_diff = soup.select('h1.title')
    result['name'] = name_diff[0].get_text().strip()
    result['diff'] = float(name_diff[1].get_text().strip()[1:-1])
    update_str = soup.select_one('div.level>div.level-item:nth-child(3)').get_text()
    result['last_update'] = re.search(r'Last update (\d+\S+) ago', update_str).groups(0)[0]

    # player stat
    stat = soup.select('nav.level>div.has-text-centered>div')
    result['records'] = int(stat[0].select_one('p:nth-child(2)').get_text().strip())
    result['perfects'] = int(stat[1].select_one('p:nth-child(2)').get_text().strip())
    result['avg'] = float(stat[2].select_one('p:nth-child(2)').get_text().strip()[:-2])

    result['songs'] = []
    # songs stat
    for i in soup.select('nav.level:nth-child(n+3)'):
        song = {'icon': 'https://musedash.moe' + i.select_one('div img')['src']}
        stats = i.select('div>div')
        song['name'] = stats[0].select_one('p:nth-child(1)>span:nth-child(1)').get_text().strip()
        song['level'] = int(stats[0].select_one('p:nth-child(1)>span:nth-child(2)').get_text().strip()[3:])
        song['musician'] = stats[0].select_one('p:nth-child(2)').get_text().strip()
        song['accuracy'] = float(stats[1].select_one('p:nth-child(1)').get_text().strip()[:-1])
        song['score'] = int(stats[1].select_one('p:nth-child(2)').get_text().strip())
        chr_sprite = stats[1].select_one('p:nth-child(3)').get_text().strip().split('/')
        song['character'] = chr_sprite[0].strip()
        song['sprite'] = chr_sprite[1].strip()
        song['platform_rank'] = int(stats[2].select_one('a:nth-child(1)').get_text().strip()[1:])
        song['total_rank'] = int(stats[2].select_one('a:nth-child(2)').get_text().strip()[5:])
        result['songs'].append(song)

    return result


async def generate_muse_dash_player_image(player_id: str, image_type: Literal['png', 'jpeg'] = 'png') -> bytes:
    page = await get_new_page(viewport={'width': 1000, 'height': 2250})
    await page.goto(f'https://musedash.moe/player/{player_id}', wait_until='networkidle')
    await page.evaluate("document.querySelector('.navbar').remove()")
    ret = await page.screenshot(type=image_type)
    await page.close()
    return ret

async def _test():
    with open('test.png', 'wb') as f:
        f.write(await generate_muse_dash_player_image('test your player id', 'png'))


asyncio.run(_test())

__all__ = ['init_web_client',
           'search_muse_dash_player_id',
           'fetch_muse_dash_player_data',
           'generate_muse_dash_player_image']
