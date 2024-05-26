import re
from typing import Literal

from bs4 import BeautifulSoup
from nonebot_plugin_alconna import UniMessage, Image, Text

from essentials.libraries import render_by_browser, util


async def search_muse_dash_player_id(player_name: str) -> str | None:
    data: list[list[str]] = await util.fetch_json_data(
        f"https://api.musedash.moe/search/{player_name}"
    )
    if data and len(data) != 0 and data[0][0] == player_name:
        return data[0][1]
    return None


async def fetch_muse_dash_player_data(player_id: str) -> dict | None:
    if txt := await util.fetch_text_data(
        f"https://musedash.moe/player/{player_id}?lang=ChineseS"
    ):
        return _parse_muse_dash_page(txt)
    return None


def _parse_muse_dash_page(content: str) -> dict:
    soup = BeautifulSoup(content, "html.parser")
    result = {}
    # player name and diff
    name_diff = soup.select("h1.title")
    result["name"] = name_diff[0].get_text().strip()
    result["diff"] = float(name_diff[1].get_text().strip()[1:-1])
    update_str = soup.select_one("div.level>div.level-item:nth-child(3)").get_text()
    result["last_update"] = re.search(r"Last update (\d+\S+) ago", update_str).groups(
        0
    )[0]

    # player stat
    stat = soup.select("nav.level>div.has-text-centered>div")
    result["records"] = int(stat[0].select_one("p:nth-child(2)").get_text().strip())
    result["perfects"] = int(stat[1].select_one("p:nth-child(2)").get_text().strip())
    result["avg"] = float(stat[2].select_one("p:nth-child(2)").get_text().strip()[:-2])

    result["songs"] = []
    # songs stat
    for i in soup.select("nav.level:nth-child(n+3)"):
        song = {"icon": "https://musedash.moe" + i.select_one("div img")["src"]}
        stats = i.select("div>div")
        song["name"] = (
            stats[0].select_one("p:nth-child(1)>span:nth-child(1)").get_text().strip()
        )
        song["level"] = int(
            stats[0]
            .select_one("p:nth-child(1)>span:nth-child(2)")
            .get_text()
            .strip()[3:]
        )
        song["musician"] = stats[0].select_one("p:nth-child(2)").get_text().strip()
        song["accuracy"] = float(
            stats[1].select_one("p:nth-child(1)").get_text().strip()[:-1]
        )
        song["score"] = int(stats[1].select_one("p:nth-child(2)").get_text().strip())
        chr_sprite = stats[1].select_one("p:nth-child(3)").get_text().strip().split("/")
        song["character"] = chr_sprite[0].strip()
        song["sprite"] = chr_sprite[1].strip()
        song["platform_rank"] = int(
            stats[2].select_one("a:nth-child(1)").get_text().strip()[1:]
        )
        song["total_rank"] = int(
            stats[2].select_one("a:nth-child(2)").get_text().strip()[5:]
        )
        result["songs"].append(song)

    return result


async def generate_muse_dash_player_image(
    player_id: str, image_type: Literal["png", "jpeg"] = "png"
) -> bytes:
    page = await render_by_browser.get_new_page(
        viewport={"width": 1000, "height": 2250}
    )
    await page.goto(
        f"https://musedash.moe/player/{player_id}", wait_until="networkidle"
    )
    await page.evaluate("document.querySelector('.navbar').remove()")
    ret = await page.screenshot(type=image_type)
    await page.close()
    return ret


async def generate_muse_dash_message(player_id: str) -> UniMessage | None:
    """
    生成消息

    :param player_id: 玩家 ID

    :return: 消息
    """
    if player_id:
        if data := await fetch_muse_dash_player_data(player_id):
            ret_msg = UniMessage()
            ret_msg.append(
                Text(
                    f'玩家名：{data["name"]}\n'
                    + f'偏差值: {data["diff"]}\n'
                    + f'记录条数: {data["records"]}\n'
                    + f'完美数: {data["perfects"]}\n'
                    + f'平均准确率: {data["avg"]}%\n'
                    + f'上次更新: {data["last_update"]} 前\n'
                )
            )
            for song in data["songs"]:
                ret_msg.append(Text(util.MESSAGE_SPLIT_LINE + "\n"))
                if await util.can_send_segment(Image):
                    ret_msg.append(Image(url=song["icon"]))
                ret_msg.append(
                    Text(
                        f'曲目: {song["name"]} (Lv.{song["level"]})\n'
                        + f'作曲家: {song["musician"]}\n'
                        + f'准确度: {song["accuracy"]}%\n'
                        + f'得分: {song["score"]}\n'
                        + f'角色: {song["character"]}\n'
                        + f'精灵: {song["sprite"]}\n'
                        + f'总排名: {song["total_rank"]}\n'
                    )
                )
            return ret_msg
    return None


__all__ = [
    "search_muse_dash_player_id",
    "fetch_muse_dash_player_data",
    "generate_muse_dash_player_image",
]
