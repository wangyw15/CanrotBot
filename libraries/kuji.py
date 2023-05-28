import asyncio
import base64
import json
import random
from pathlib import Path
from typing import Tuple, Literal

from nonebot import logger

from .render_by_browser import render_html

_kuji_assets_path = Path(__file__).parent.parent / 'assets/kuji'
_kuji_data: list[dict[str, str]] = []


def _load_kuji_assets() -> None:
    global _kuji_data
    if not _kuji_data:
        with open(_kuji_assets_path / 'kuji.json', 'r', encoding='utf-8') as f:
            _kuji_data = json.load(f)
            logger.info(f'kuji data: {len(_kuji_data)}')


async def generate_kuji(image_type: Literal['png', 'jpeg'] | None = 'png') -> Tuple[str, dict[str, str]]:
    _load_kuji_assets()
    selected_kuji: dict[str, str] = random.choice(_kuji_data)

    # without image
    if not image_type:
        return '', selected_kuji

    # generate html
    with open(_kuji_assets_path / 'template.html', 'r', encoding='utf-8') as f:
        generated_html = f.read()

    generated_content = ''
    for i in range(len(selected_kuji['content'])):
        generated_content += \
            f'<div class="content center" style="grid-column: {5-i};">{selected_kuji["content"][i]}</div>'
    generated_mean = ''.join([f'<p>{x.split("：")[0]}<br /><span>{x.split("：")[1]}</span></p>'
                              for x in selected_kuji['mean']])
    generated_html = generated_html\
        .replace('{{count}}', selected_kuji['count'])\
        .replace('{{type}}', selected_kuji['type'])\
        .replace('{{content}}', generated_content)\
        .replace('{{straight}}', selected_kuji['straight'])\
        .replace('{{mean}}', generated_mean)
    img = await render_html(generated_html, _kuji_assets_path, image_type=image_type,
                            viewport={'width': 520, 'height': 820})
    return base64.b64encode(img).decode('utf-8'), selected_kuji


def generate_kuji_str(content: dict[str, str]) -> str:
    result = f"日本东京浅草寺观音灵签{content['count']} {content['type']}\n" \
             f"    {content['content'][0]}，{content['content'][1]}；\n" \
             f"    {content['content'][2]}，{content['content'][3]}。\n" \
             f"〖四句解说〗\n" \
             f"    {content['straight']}\n" \
             f"〖解曰〗\n"
    result += '\n'.join(f'    ❃ {x}' for x in content['mean'])
    return result


_load_kuji_assets()


async def main():
    with open('test.png', 'wb') as f:
        f.write(base64.b64decode((await generate_kuji())[0]))

if __name__ == '__main__':
    asyncio.run(main())

