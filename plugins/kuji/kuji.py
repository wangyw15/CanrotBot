import asyncio
import json
import random
from typing import Tuple, Literal

from nonebot import logger

from essentials.libraries import render_by_browser
from storage import asset

_kuji_assets_path = asset.get_assets_path("kuji")
_kuji_data: list[dict[str, str]] = []


def _load_kuji_assets() -> None:
    global _kuji_data
    if not _kuji_data:
        with open(_kuji_assets_path / "kuji.json", "r", encoding="utf-8") as f:
            _kuji_data = json.load(f)
            logger.info(f"kuji data: {len(_kuji_data)}")


async def generate_kuji(
    image_type: Literal["png", "jpeg", ""] | None = "png"
) -> Tuple[bytes | None, dict[str, str]]:
    _load_kuji_assets()
    selected_kuji: dict[str, str] = random.choice(_kuji_data)

    # without image
    if not image_type:
        return None, selected_kuji

    # generate html
    with open(_kuji_assets_path / "template.html", "r", encoding="utf-8") as f:
        generated_html = f.read().replace(
            "'{DATA_HERE}'", json.dumps(selected_kuji, ensure_ascii=False)
        )
    img = await render_by_browser.render_html(
        generated_html,
        _kuji_assets_path,
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


_load_kuji_assets()


async def main():
    with open("test.png", "wb") as f:
        f.write((await generate_kuji())[0])


if __name__ == "__main__":
    asyncio.run(main())
