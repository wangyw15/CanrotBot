from datetime import datetime

import httpx
from bs4 import BeautifulSoup

_client = httpx.AsyncClient()
_idols: list[dict[str, str]] = []


async def get_idols() -> list[dict[str, str]]:
    global _idols
    if not _idols:
        resp = await _client.get(
            "https://wiki.biligame.com/idolypride/%E8%A7%92%E8%89%B2%E5%9B%BE%E9%89%B4"
        )
        if resp.is_success and resp.status_code == 200:
            soup = BeautifulSoup(resp.text)
            for group in soup.select("div.char"):
                group_name = group.select_one("div:first-child span").text.split()[0]
                for character in group.select(".sawimg>a"):
                    _idols.append(
                        {
                            "name": character.attrs["title"],
                            "group": group_name,
                            "portrait": character.select_one("img").attrs["src"],
                            "page": "https://wiki.biligame.com"
                            + character.attrs["href"],
                        }
                    )
    return _idols


async def get_full_calendar() -> list[dict]:
    resp = await _client.get(
        "https://wiki.biligame.com/idolypride/api.php?"
        "action=expandtemplates&"
        "format=json&"
        "text=%7B%7B%23invoke%3A%E6%97%A5%E5%8E%86%E5%87%BD%E6%95%B0%7CgetAllData%7D%7D"
    )
    if resp.is_success and resp.status_code == 200:
        data = resp.json()["expandtemplates"]["*"]
        # 处理csv
        table: list[list[str]] = [line.split(",") for line in data.split(";") if line]
        ret: list[dict] = []
        for row in table:
            ret.append(
                {
                    "start": datetime.strptime(row[0], "%Y/%m/%d"),
                    "end": datetime.strptime(row[1], "%Y/%m/%d"),
                    "name": row[2],
                    "type": row[3],
                    "page": row[4],
                    "color": row[5],
                }
            )
        return ret
    return []


async def get_today_events() -> list[dict]:
    data = await get_full_calendar()
    ret: list[dict] = []
    for i in data:
        if i["start"].date() <= datetime.now().date() <= i["end"].date():
            ret.append(i)
    return ret


async def main():
    print(await get_idols())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
