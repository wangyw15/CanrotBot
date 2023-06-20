import urllib.parse

import httpx
from nonebot import get_driver
from pydantic import BaseModel, validator

from adapters import unified
from essentials.libraries import util


class SearchImageConfig(BaseModel):
    canrot_proxy: str = ""
    saucenao_api_key: str = ""
    search_result_count: int = 1

    @validator("saucenao_api_key")
    def saucenao_api_key_validator(cls, v):
        if (not v) or (not isinstance(v, str)):
            raise ValueError("saucenao_api_key must be a str")
        return v

    @validator("search_result_count")
    def search_result_count_validator(cls, v):
        if (not v) or (not isinstance(v, int)):
            raise ValueError("search_result_count must be a int")
        return v


_config = SearchImageConfig.parse_obj(get_driver().config)


if _config.canrot_proxy:
    _client = httpx.AsyncClient(proxies=_config.canrot_proxy)
else:
    _client = httpx.AsyncClient()
_client.timeout = 10


def generate_message_from_saucenao_result(api_result: dict) -> unified.Message:
    msg = unified.Message()

    # limit
    if "header" in api_result:
        msg += "搜图次数限制: \n"
        header: dict = api_result["header"]
        if "long_remaining" in header:
            if header["long_remaining"] < 1:
                return unified.Message("今日搜索次数已用完")
            msg += f'今日剩余（每日重置）: {header["long_remaining"]}\n'
        if "short_remaining" in header:
            if header["short_remaining"] < 1:
                return unified.Message("30秒内搜索次数已用完")
            msg += f'当前剩余（半分钟重置）: {header["short_remaining"]}\n'

    # results
    msg += "搜图结果: \n"
    results: list[dict] = api_result["results"]
    for api_result in results:
        # split line
        msg += util.MESSAGE_SPLIT_LINE + "\n"

        header: dict = api_result["header"]
        data: dict = api_result["data"]

        # thumbnail
        if "thumbnail" in header:
            msg += "缩略图: \n"
            msg += unified.MessageSegment.image(header["thumbnail"])

        # similarity
        msg += "相似度: " + header["similarity"] + "%\n"

        # video
        if "est_time" in data:
            # title prompt
            if "anidb_aid" in data or "mal_id" in data or "anilist_id" in data:
                # anime data
                msg += "动漫: "
            elif "imdb_id" in data:
                # imdb data
                msg += "剧集: "
            # title
            if "source" in data:
                msg += data["source"]
            # year
            if "year" in data:
                msg += f' ({data["year"]}年)'
            msg += "\n"
            if "jp_name" in data:
                msg += f'日文名: {data["jp_name"]}\n'
            if "eng_name" in data:
                msg += f'英文名: {data["eng_name"]}\n'
            # episode
            if "part" in data and data["part"]:
                msg += f'集数: {data["part"]}\n'
            # est time
            if "est_time" in data:
                msg += f'时间: {data["est_time"]}\n'
            # urls
            if "ext_urls" in data:
                msg += "链接: \n"
                for url in data["ext_urls"]:
                    msg += url + "\n"
            continue

        # pixiv
        if "pixiv_id" in data:
            # title
            msg += "Pixiv: "
            if "title" in data:
                msg += data["title"]
            msg += "\n"
            # author name
            if "member_name" in data:
                msg += f'作者: {data["member_name"]}\n'
            # artwork id
            if "pixiv_id" in data:
                msg += f'图片链接: \nhttps://www.pixiv.net/artworks/{data["pixiv_id"]}\n'
            # author id
            if "member_id" in data:
                msg += f'作者链接: \nhttps://www.pixiv.net/users/{data["member_id"]}\n'
            continue

        # patreon
        if "service" in data and data["service"] == "patreon":
            msg += "Patreon: "
            if "title" in data:
                msg += data["title"]
            msg += "\n"
            if "user_name" in data:
                msg += f'作者: {data["user_name"]}\n'
            if "id" in data:
                msg += f'作品链接: https://www.patreon.com/posts/{data["id"]}\n'
            if "user_id" in data:
                msg += f'作者链接: https://www.patreon.com/user?u={data["user_id"]}\n'
            continue

        # deviant art
        if "da_id" in data:
            msg += "DeviantArt: "
            if "title" in data:
                msg += data["title"]
            msg += "\n"
            # author name
            if "author_name" in data:
                msg += f'作者: {data["author_name"]}\n'
            # artwork page
            msg += f'图片链接: https://deviantart.com/view/{data["da_id"]}\n'
            # author home page
            if "author_url" in data:
                msg += f'作者链接: {data["author_url"]}\n'
            continue

        # fur affinity
        if "fa_id" in data:
            msg += "Fur Affinity: "
            if "title" in data:
                msg += data["title"]
            msg += "\n"
            # author name
            if "author_name" in data:
                msg += f'作者: {data["author_name"]}\n'
            # artwork page
            msg += f'图片链接: https://www.furaffinity.net/view/{data["fa_id"]}\n'
            # author home page
            if "author_url" in data:
                msg += f'作者链接: {data["author_url"]}\n'
            continue

        # art station
        if "as_project" in data:
            msg += "Art Station: "
            if "title" in data:
                msg += data["title"]
            msg += "\n"
            # author name
            if "author_name" in data:
                msg += f'作者: {data["author_name"]}\n'
            # artwork page
            msg += f'图片链接: https://www.artstation.com/artwork/{data["as_project"]}\n'
            # author home page
            if "author_url" in data:
                msg += f'作者链接: {data["author_url"]}\n'
            continue

        # manga
        if "type" in data and data["type"] == "Manga":
            msg += "漫画: "
            if "source" in data:
                msg += data["source"]
            msg += "\n"
            if "part" in data:
                msg += f'话数: {data["part"]}\n'
            if "ext_urls" in data:
                msg += "链接: \n"
                for url in data["ext_urls"]:
                    msg += url + "\n"
            continue

        # general information
        # title
        if "title" in data:
            msg += f'名称: {data["title"]}\n'
        elif "source" in data:
            msg += f'名称: {data["source"]}\n'
        if "eng_name" in data:
            msg += f'英文名: {data["eng_name"]}\n'
        if "jp_name" in data:
            msg += f'日文名: {data["jp_name"]}\n'

        # author
        if "creator_name" in data and data["creator_name"]:
            msg += f'作者: {data["creator_name"]}'
            if "creator" in data and data["creator"]:
                if isinstance(data["creator"], str):
                    msg += f' ({data["creator"]})'
            msg += "\n"
        elif "creator_name" in data and isinstance(data["creator"], list):
            msg += " ("
            for creator in data["creator"]:
                msg += creator + ", "
            msg += ")"
        if "author_name" in data and data["author_name"]:
            msg += f'作者: {data["author_name"]}\n'
        if "author_url" in data and data["author_url"]:
            msg += f'作者链接: {data["author_url"]}\n'

        # urls
        if "ext_urls" in data:
            msg += "链接: \n"
            for url in data["ext_urls"]:
                msg += url + "\n"
    return msg


def generate_message_from_tracemoe_result(api_result: dict) -> unified.Message:
    msg = unified.Message()
    if api_result["error"]:
        return "搜索失败: " + api_result["error"]
    msg += f'已搜索 {api_result["frameCount"]} 帧\n'
    for result in api_result["result"][0: _config.search_result_count]:
        msg += util.MESSAGE_SPLIT_LINE + "\n"
        msg += unified.MessageSegment.image(result["image"])
        msg += f'相似度: {round(result["similarity"]*100, 2)}%\n'
        msg += f'番剧文件名: {result["filename"]}\n'
        msg += f'第 {result["episode"]} 集\n'
        msg += (
            f'时间: {util.seconds_to_time(result["from"])}~{util.seconds_to_time(result["to"])}\n'
        )
        msg += f'AniList 链接: https://anilist.co/anime/{result["anilist"]}\n'
    return msg


async def search_image_from_saucenao(img_url: str) -> dict | None:
    api_url = "https://saucenao.com/search.php?db=999&output_type=2&testmode=1&numres={numres}&api_key={api_key}&url={url}"
    resp = await _client.get(
        api_url.format(
            api_key=_config.saucenao_api_key,
            url=urllib.parse.quote_plus(img_url),
            numres=_config.search_result_count,
        )
    )
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None


async def search_image_from_tracemoe(img_url: str) -> dict | None:
    api_url = "https://api.trace.moe/search?url={url}"
    resp = await _client.get(api_url.format(url=urllib.parse.quote_plus(img_url)))
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None
