import re
from typing import Literal

from httpx import AsyncClient

from canrotbot.llm.tools import register_tool

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


@register_tool("bilibili_fetch_video_data")
async def fetch_video_data(vid: str) -> dict | None:
    """
    获取Bilibili的视频av号或bv号对应的视频信息

    Args:
        vid: av号或bv号

    Returns:
        视频信息，如果获取失败则返回None
    """
    url = ""
    if vid.lower().startswith("bv"):
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={vid}"
    elif vid.lower().startswith("av"):
        url = f"https://api.bilibili.com/x/web-interface/view?aid={vid[2:]}"
    if not url:
        return None
    raw_data = await fetch_json_data(url, headers=_header)
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


@register_tool("bilibili_fetch_all_projects")
async def fetch_all_projects(
    area: str = "310000",
    project_type: Literal["全部类型", "演出", "展览", "本地生活"] = "全部类型",
    limit: int = 0,
) -> list[dict]:
    """
    从Bilibili会员购页面上，根据给定的地区，获取漫展、演出等活动

    Args:
        area: 地区代码（默认为上海，地区代码310000）
        project_type: 活动类型，有全部类型、演出、展览、本地生活，默认为全部类型
        limit: 返回条目数量限制；为0代表不限制数量，默认为10

    Returns:
        活动列表
    """
    first_page = await fetch_json_data(
        _projects_url.format(page=1, area=area, project_type=project_type)
    )
    if first_page and first_page["errno"] == 0:
        total_pages = first_page["data"]["numPages"]
        result: list[dict] = first_page["data"]["result"]
        for page in range(2, total_pages + 1):
            if len(result) >= limit:
                break

            page_data = await fetch_json_data(
                _projects_url.format(page=page, area=area, project_type=project_type)
            )
            if page_data and page_data["errno"] == 0:
                result.extend(page_data["data"]["result"])
        return result
    return []
