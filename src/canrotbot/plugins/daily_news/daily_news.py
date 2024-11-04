from datetime import datetime

from canrotbot.essentials.libraries import network


async def get_daily_news() -> dict | None:
    return await network.fetch_json_data("https://60s.viki.moe/?v2=1")


def generate_news_message(news: dict, with_url: bool = True) -> str | None:
    if news["status"] != 200:
        return None

    ret = ""

    for n, i in enumerate(news["data"]["news"]):
        ret += f"{n+1}. {i}\n"

    if with_url:
        ret += "\n\n来源：" + news["data"]["url"]

    ret += "\n更新时间：" + datetime.fromtimestamp(
        news["data"]["updated"] / 1000
    ).strftime("%Y-%m-%d %H:%M:%S")

    return ret
