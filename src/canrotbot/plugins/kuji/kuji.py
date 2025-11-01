import random
from typing import Tuple, Literal

from jinja2 import Template
from nonebot import logger, get_driver

from canrotbot.essentials.libraries import file, path, render_by_browser

ASSET_PATH = path.get_asset_path("kuji")
KUJI_DATA: list[dict[str, str]] = []


@get_driver().on_startup
async def _load_kuji_assets() -> None:
    global KUJI_DATA
    if not KUJI_DATA:
        KUJI_DATA = file.read_json(ASSET_PATH / "kuji.json")
        logger.info(f"kuji data: {len(KUJI_DATA)}")


async def generate_kuji(
    image_type: Literal["png", "jpeg"] | None = "png"
) -> Tuple[bytes | None, dict[str, str]]:
    _load_kuji_assets()
    selected_kuji: dict[str, str] = random.choice(KUJI_DATA)

    # without image
    if not image_type:
        return None, selected_kuji

    # generate html
    template: Template = Template((ASSET_PATH / "template.jinja").read_text(encoding="utf-8"))
    img = await render_by_browser.render_html(
        template.render(kuji=selected_kuji),
        ASSET_PATH,
        image_type=image_type,
        viewport={"width": 520, "height": 820},
    )
    return img, selected_kuji


def generate_kuji_str(content: dict[str, str]) -> str:
    result = (
        f"日本东京浅草寺观音灵签{content['count']} {content['type']}\n"
        f"    {content['content'][0]}，{content['content'][1]}；\n"
        f"    {content['content'][2]}，{content['content'][3]}。\n"
        f"〖四句解说〗\n"
        f"    {content['straight']}\n"
        f"〖解曰〗\n"
    )
    result += "\n".join(f"    ❃ {x}" for x in content["mean"])
    return result
