import urllib.parse
from datetime import datetime

from nonebot import get_plugin_config
from nonebot_plugin_alconna import Image, Text, UniMessage

from canrotbot.essentials.libraries import network, util

from .config import SearchImageConfig

AVAILABLE_API = {
    "saucenao": "https://saucenao.com/search.php?db=999&output_type=2&testmode=1&numres={numres}&api_key={api_key}&url={url}",
    "tracemoe": "https://api.trace.moe/search?url={url}",
}

config = get_plugin_config(SearchImageConfig)


def timestamp_to_str(seconds: int) -> str:
    return datetime.fromtimestamp(seconds).strftime("%Y-%m-%d %H:%M:%S")


async def generate_message_from_saucenao_result(
    api_result: dict, with_url: bool = True
) -> UniMessage:
    # TODO 重构搜图消息
    msg = UniMessage()

    # limit
    if "header" in api_result:
        msg += Text("搜图次数限制: \n")
        header: dict = api_result["header"]
        if "long_remaining" in header:
            if header["long_remaining"] < 1:
                return UniMessage(Text("今日搜索次数已用完"))
            msg += Text(f'今日剩余（每日重置）: {header["long_remaining"]}\n')
        if "short_remaining" in header:
            if header["short_remaining"] < 1:
                return UniMessage(Text("30秒内搜索次数已用完"))
            msg += Text(f'当前剩余（半分钟重置）: {header["short_remaining"]}\n')

    # results
    msg += Text("搜图结果: \n")
    results: list[dict] = api_result["results"]
    for api_result in results:
        # split line
        msg += Text(util.MESSAGE_SPLIT_LINE + "\n")

        header: dict = api_result["header"]
        data: dict = api_result["data"]

        # thumbnail
        if "thumbnail" in header and await util.can_send_segment(Image):
            msg += Text("缩略图: \n")
            msg += Image(url=header["thumbnail"])

        # similarity
        msg += Text("相似度: " + header["similarity"] + "%\n")

        # video
        if "est_time" in data:
            # title prompt
            if "anidb_aid" in data or "mal_id" in data or "anilist_id" in data:
                # anime data
                msg += Text("动漫: ")
            elif "imdb_id" in data:
                # imdb data
                msg += Text("剧集: ")
            # title
            if "source" in data:
                msg += Text(data["source"])
            # year
            if "year" in data:
                msg += Text(f' ({data["year"]}年)')
            msg += Text("\n")
            if "jp_name" in data:
                msg += Text(f'日文名: {data["jp_name"]}\n')
            if "eng_name" in data:
                msg += Text(f'英文名: {data["eng_name"]}\n')
            # episode
            if "part" in data and data["part"]:
                msg += Text(f'集数: {data["part"]}\n')
            # est time
            if "est_time" in data:
                msg += Text(f'时间: {data["est_time"]}\n')
            # urls
            if "ext_urls" in data and with_url:
                msg += Text("链接: \n")
                for url in data["ext_urls"]:
                    msg += Text(url + "\n")
            continue

        # pixiv
        if "pixiv_id" in data:
            # title
            msg += Text("Pixiv: ")
            if "title" in data:
                msg += Text(data["title"])
            msg += Text("\n")
            # author name
            if "member_name" in data:
                msg += Text(f'作者: {data["member_name"]}\n')
            # artwork id
            if "pixiv_id" in data and with_url:
                msg += Text(
                    f'图片链接: \nhttps://www.pixiv.net/artworks/{data["pixiv_id"]}\n'
                )
            # author id
            if "member_id" in data and with_url:
                msg += Text(
                    f'作者链接: \nhttps://www.pixiv.net/users/{data["member_id"]}\n'
                )
            continue

        # patreon
        if "service" in data and data["service"] == "patreon":
            msg += Text("Patreon: ")
            if "title" in data:
                msg += Text(data["title"])
            msg += Text("\n")
            if "user_name" in data:
                msg += Text(f'作者: {data["user_name"]}\n')
            if "id" in data and with_url:
                msg += Text(f'作品链接: https://www.patreon.com/posts/{data["id"]}\n')
            if "user_id" in data and with_url:
                msg += Text(
                    f'作者链接: https://www.patreon.com/user?u={data["user_id"]}\n'
                )
            continue

        # deviant art
        if "da_id" in data:
            msg += Text("DeviantArt: ")
            if "title" in data:
                msg += Text(data["title"])
            msg += Text("\n")
            # author name
            if "author_name" in data:
                msg += Text(f'作者: {data["author_name"]}\n')
            # artwork page
            if with_url:
                msg += Text(f'图片链接: https://deviantart.com/view/{data["da_id"]}\n')
            # author home page
            if "author_url" in data and with_url:
                msg += Text(f'作者链接: {data["author_url"]}\n')
            continue

        # fur affinity
        if "fa_id" in data:
            msg += Text("Fur Affinity: ")
            if "title" in data:
                msg += Text(data["title"])
            msg += Text("\n")
            # author name
            if "author_name" in data:
                msg += Text(f'作者: {data["author_name"]}\n')
            # artwork page
            msg += Text(f'图片链接: https://www.furaffinity.net/view/{data["fa_id"]}\n')
            # author home page
            if "author_url" in data and with_url:
                msg += Text(f'作者链接: {data["author_url"]}\n')
            continue

        # art station
        if "as_project" in data:
            msg += Text("Art Station: ")
            if "title" in data:
                msg += Text(data["title"])
            msg += Text("\n")
            # author name
            if "author_name" in data:
                msg += Text(f'作者: {data["author_name"]}\n')
            # artwork page
            if with_url:
                msg += Text(
                    f'图片链接: https://www.artstation.com/artwork/{data["as_project"]}\n'
                )
            # author home page
            if "author_url" in data and with_url:
                msg += Text(f'作者链接: {data["author_url"]}\n')
            continue

        # manga
        if "type" in data and data["type"] == "Manga":
            msg += Text("漫画: ")
            if "source" in data:
                msg += Text(data["source"])
            msg += Text("\n")
            if "part" in data:
                msg += Text(f'话数: {data["part"]}\n')
            if "ext_urls" in data and with_url:
                msg += Text("链接: \n")
                for url in data["ext_urls"]:
                    msg += Text(url + "\n")
            continue

        # general information
        # title
        if "title" in data:
            msg += Text(f'名称: {data["title"]}\n')
        elif "source" in data and (data["source"].startswith("http") and with_url):
            msg += Text(f'来源: {data["source"]}\n')
        if "eng_name" in data:
            msg += Text(f'英文名: {data["eng_name"]}\n')
        if "jp_name" in data:
            msg += Text(f'日文名: {data["jp_name"]}\n')

        # author
        if "creator_name" in data and data["creator_name"]:
            msg += Text(f'作者: {data["creator_name"]}')
            if "creator" in data and data["creator"]:
                if isinstance(data["creator"], str):
                    msg += Text(f' ({data["creator"]})')
            msg += Text("\n")
        elif "creator_name" in data and isinstance(data["creator"], list):
            msg += Text(" (")
            for creator in data["creator"]:
                msg += Text(creator + ", ")
            msg += Text(")")
        if "author_name" in data and data["author_name"]:
            msg += Text(f'作者: {data["author_name"]}\n')
        if "author_url" in data and data["author_url"] and with_url:
            msg += Text(f'作者链接: {data["author_url"]}\n')

        # urls
        if "ext_urls" in data and with_url:
            msg += Text("链接: \n")
            for url in data["ext_urls"]:
                msg += Text(url + "\n")
    return msg


async def generate_message_from_tracemoe_result(
    api_result: dict, with_url: bool = True
) -> UniMessage:
    msg = UniMessage()
    if api_result["error"]:
        return UniMessage(Text("搜索失败: " + api_result["error"]))
    msg += Text(f'已搜索 {api_result["frameCount"]} 帧\n')
    for result in api_result["result"][0 : config.search_result_count]:
        msg += Text(util.MESSAGE_SPLIT_LINE + "\n")
        if await util.can_send_segment(Image):
            msg += Image(url=result["image"])
        msg += Text(f'相似度: {round(result["similarity"]*100, 2)}%\n')
        msg += Text(f'番剧文件名: {result["filename"]}\n')
        msg += Text(f'第 {result["episode"]} 集\n')
        msg += Text(
            f'时间: {timestamp_to_str(result["from"])}~{timestamp_to_str(result["to"])}\n'
        )
        if with_url:
            msg += Text(f'AniList 链接: https://anilist.co/anime/{result["anilist"]}\n')
    return msg


async def search_image_from_saucenao(img_url: str) -> dict | None:
    url = AVAILABLE_API["saucenao"].format(
        api_key=config.saucenao_api_key,
        url=urllib.parse.quote_plus(img_url),
        numres=config.search_result_count,
    )
    return await network.fetch_json_data(url)


async def search_image_from_tracemoe(img_url: str) -> dict | None:
    url = AVAILABLE_API["tracemoe"].format(url=urllib.parse.quote_plus(img_url))
    return await network.fetch_json_data(url)
