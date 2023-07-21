import re
from typing import Literal

from httpx import Response, AsyncClient

_client = AsyncClient()
_projects_url = 'https://show.bilibili.com/api/ticket/project/listV3' \
                '?page={page}&pagesize=20&platform=web&area={area}&p_type={project_type}&style=1'
bilibili_vid_pattern = r'(?:https?:\/\/)?(?:(?:www\.)?bilibili.com\/video|b23\.tv)\/((?:BV|av)[0-9A-Za-z]+)'


async def _fetch_json_data(url: str) -> dict | None:
    """从URL获取json数据"""
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None


async def fetch_video_data(vid: str) -> dict | None:
    resp: Response | None = None
    if vid.startswith('BV'):
        resp = await _client.get(f'https://api.bilibili.com/x/web-interface/view?bvid={vid}')
    elif vid.startswith('av'):
        resp = await _client.get(f'https://api.bilibili.com/x/web-interface/view?aid={vid}')
    if resp and resp.is_success and resp.status_code == 200:
        data = resp.json()
        if data['code'] == 0:
            return data['data']
    return None


async def get_bvid_from_short_link(url: str) -> str | None:
    resp = await _client.get(url, follow_redirects=False)
    if resp.status_code == 302:
        return re.match(bilibili_vid_pattern, resp.headers['Location']).groups()[0]
    return None


async def fetch_all_projects(area: str = '310000',
                             project_type: Literal['全部类型', '演出', '展览', '本地生活'] = '全部类型') -> list[dict]:
    first_page = await _fetch_json_data(_projects_url.format(page=1, area=area, project_type=project_type))
    if first_page and first_page['errno'] == 0:
        total_pages = first_page['data']['numPages']
        result: list[dict] = first_page['data']['result']
        for page in range(2, total_pages + 1):
            page_data = await _fetch_json_data(
                _projects_url.format(page=page, area=area, project_type=project_type))
            if page_data and page_data['errno'] == 0:
                result.extend(page_data['data']['result'])
        return result
    return []


async def main() -> None:
    projects = await fetch_all_projects()
    if projects:
        for i in projects:
            print(i['project_name'])

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
