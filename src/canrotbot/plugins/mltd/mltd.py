import json
import random

from canrotbot.essentials.libraries import path, render_by_browser
from canrotbot.libraries.mltd import cards_for_gasha

ASSET_PATH = path.get_asset_path("mltd")


async def generate_card_info_image(card: dict) -> bytes:
    html = (
        (ASSET_PATH / "card_info.html")
        .read_text(encoding="utf-8")
        .replace("'{DATA_HERE}'", json.dumps(card))
    )
    return await render_by_browser.render_html(
        html, ASSET_PATH, viewport={"width": 1280, "height": 1000}
    )


async def gasha() -> tuple[bytes, list[dict]] | None:
    if not cards_for_gasha:
        return None

    cards: list[dict] = []
    # SR保底
    got_sr_or_better = False
    # 抽卡
    while len(cards) != 10:
        magic_number = random.random()
        if magic_number < 0.03:
            cards.append(random.choice(cards_for_gasha[4]))
            got_sr_or_better = True
        elif magic_number < 0.15:
            cards.append(random.choice(cards_for_gasha[3]))
            got_sr_or_better = True
        else:
            cards.append(random.choice(cards_for_gasha[2]))
    # SR保底
    if not got_sr_or_better:
        cards[random.randint(0, 9)] = random.choice(cards_for_gasha[3])
    # 生成图片
    html = (
        (ASSET_PATH / "gasha.html")
        .read_text(encoding="utf-8")
        .replace("'{DATA_HERE}'", json.dumps(cards))
    )
    img = await render_by_browser.render_html(
        html, ASSET_PATH, viewport={"width": 1920, "height": 1080}
    )
    return img, cards
