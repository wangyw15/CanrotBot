import re
from typing import Literal

from httpx import AsyncClient

_client = AsyncClient()
_projects_url = (
    "https://show.bilibili.com/api/ticket/project/listV3"
    "?page={page}&pagesize=20&platform=web&area={area}&p_type={project_type}&style=1"
)
_header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5666.197 Safari/537.36"
}

bilibili_vid_pattern = r"(?:https?:\/\/)?(?:(?:www\.)?bilibili.com\/video|b23\.tv)\/((?:[AaBb][Vv])[0-9A-Za-z]+)"
short_link_pattern = r"https:\/\/b23.tv\/(?!BV)[0-9A-Za-z]{7}"


async def fetch_json_data(url: str) -> dict | None:
    """
    从URL获取json数据

    :param url: URL

    :return: JSON 内容
    """
    resp = await _client.get(url, headers=_header)
    if resp.is_success and resp.status_code == 200:
        return resp.json()


async def fetch_video_data(vid: str) -> dict | None:
    """
    获取av号或bv号对应的视频信息

    :param vid: av号或bv号

    :return: 视频信息，如果获取失败则返回None
    """
    url = ""
    if vid.lower().startswith("bv"):
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={vid}"
    elif vid.lower().startswith("av"):
        url = f"https://api.bilibili.com/x/web-interface/view?aid={vid[2:]}"
    if not url:
        return None
    raw_data = await fetch_json_data(url)
    if raw_data and raw_data["code"] == 0:
        return raw_data["data"]
    return None


async def get_bvid_from_short_link(url: str) -> str | None:
    """
    从短链接获取bv号

    :param url: 短链接

    :return: bv号
    """
    resp = await _client.get(url, follow_redirects=False)
    if resp.status_code == 302:
        return re.match(bilibili_vid_pattern, resp.headers["Location"]).groups()[0]
    return None


async def fetch_all_projects(
    area: str = "310000",
    project_type: Literal["全部类型", "演出", "展览", "本地生活"] = "全部类型",
) -> list[dict]:
    """
    获取所有活动

    :param area: 地区代号（默认上海）
    :param project_type: 活动类型

    :return: 活动列表
    """
    first_page = await fetch_json_data(
        _projects_url.format(page=1, area=area, project_type=project_type)
    )
    if first_page and first_page["errno"] == 0:
        total_pages = first_page["data"]["numPages"]
        result: list[dict] = first_page["data"]["result"]
        for page in range(2, total_pages + 1):
            page_data = await fetch_json_data(
                _projects_url.format(page=page, area=area, project_type=project_type)
            )
            if page_data and page_data["errno"] == 0:
                result.extend(page_data["data"]["result"])
        return result
    return []
