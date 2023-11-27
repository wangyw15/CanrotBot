import random
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from .. import fortune

_ships: dict[str, str] = {}
_ships_last_fetch: datetime | None = None
_client = httpx.AsyncClient()


async def get_all_ships() -> dict[str, str]:
    global _ships, _ships_last_fetch
    if (
        not _ships
        or not _ships_last_fetch
        or (datetime.now() - _ships_last_fetch).total_seconds() > 3600 * 24
    ):
        resp = await _client.get(
            "https://wiki.biligame.com/blhx/%E8%88%B0%E8%88%B9%E5%9B%BE%E9%89%B4"
        )
        if resp.is_success and resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            _ships.clear()
            for i in soup.select(".jntj-1"):
                a = i.select_one(".jntj-4>a")
                _ships[a.get_text()] = "https://wiki.biligame.com" + a["href"]
            _ships_last_fetch = datetime.now()
    return _ships


async def get_random_ship_image_url() -> str | None:
    ships = await get_all_ships()
    ship: str = random.choice(list(ships.keys()))
    url: str = ships[ship]
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        return soup.select_one(".wiki-bot-img")["src"]
    return None


async def generate_fortune_html() -> str:
    with (fortune.fortune_assets_path / "template" / "azurlane.html").open(
        "r", encoding="utf-8"
    ) as f:
        return f.read().replace("{{image}}", await get_random_ship_image_url())


# 注册主题
fortune.register_theme(
    "azurlane",
    generate_fortune_html,
    ["碧蓝航线", "碧蓝", "azure", "Azure", "AzurLane", "blhx"],
)


async def main():
    ships = await get_all_ships()
    print(ships)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
