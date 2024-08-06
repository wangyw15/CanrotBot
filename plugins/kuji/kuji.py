import json
import random
from typing import Tuple, Literal

from nonebot import logger, get_driver

from essentials.libraries import file, path, render_by_browser

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
    generated_html = file.read_text(ASSET_PATH / "template.html").replace(
        "'{DATA_HERE}'", json.dumps(selected_kuji, ensure_ascii=False)
    )
    img = await render_by_browser.render_html(
        generated_html,
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
