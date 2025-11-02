import random

from jinja2 import Template

from canrotbot.essentials.libraries import path, render_by_browser
from canrotbot.libraries.mltd import get_cards_for_gasha

ASSET_PATH = path.get_asset_path("mltd")


async def generate_card_info_image(card: dict) -> bytes:
    template: Template = Template(
        (ASSET_PATH / "card_info.jinja").read_text(encoding="utf-8")
    )
    return await render_by_browser.render_html(
        template.render(card=card), ASSET_PATH, viewport={"width": 1280, "height": 1000}
    )


async def gasha() -> tuple[bytes, list[dict]] | None:
    cards_for_gasha = get_cards_for_gasha()
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
    template: Template = Template(
        (ASSET_PATH / "gasha.jinja").read_text(encoding="utf-8")
    )
    img = await render_by_browser.render_html(
        template.render(cards=cards),
        ASSET_PATH,
        viewport={"width": 1920, "height": 1080},
    )
    return img, cards
