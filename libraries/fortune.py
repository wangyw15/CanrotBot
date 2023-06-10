import base64
import json
import random
from pathlib import Path
from typing import Tuple, Literal

from nonebot import logger

from .render_by_browser import render_html

_fortune_assets_path = Path(__file__).parent.parent / "assets/fortune"
_fortune_assets_version: str = ''
_copywriting: list[dict] = []
_specific_rules: dict[str, list[str]] = {}
_themes: dict[str, list[str]] = {}


def _load_fortune_assets() -> None:
    global _fortune_assets_version
    global _copywriting
    global _specific_rules
    global _themes

    if not _fortune_assets_version or not _copywriting:
        with open(_fortune_assets_path / "fortune_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            _fortune_assets_version = str(data['version'])
            logger.info(f"fortune version: {_fortune_assets_version}")
            _copywriting = data['copywriting']
            logger.info(f"fortune copywriting: {len(_copywriting)}")

    if not _specific_rules:
        with open(_fortune_assets_path / "specific_rules.json", "r", encoding="utf-8") as f:
            _specific_rules = json.load(f)
            logger.info(f"fortune specific rules: {len(_specific_rules)}")

    if not _themes:
        with open(_fortune_assets_path / "themes.json", "r", encoding="utf-8") as f:
            _themes = json.load(f)
            logger.info(f"fortune themes: {len(_themes)}")


def _get_random_base_image(theme: str = 'random') -> Path:
    if theme == 'random' or theme not in _themes:
        theme = random.choice(list(_themes.keys()))
    theme_path = _fortune_assets_path / 'image' / theme
    return random.choice(list(theme_path.iterdir()))


def get_theme_key_from_name(name: str) -> str:
    for k, v in _themes.items():
        if name == k or name in v:
            return k
    return 'random'


async def generate_fortune(theme: str = 'random', image_type: Literal['png', 'jpeg'] = 'png',
                           title: str = '', content: str = '', rank: int = 0) -> Tuple[bytes, str, str, int]:
    """
    生成给定主题的运势图片，如果不给定运势内容则随机选择

    :param theme: 运势主题
    :param image_type: 返回图片格式
    :param title: 运势标题
    :param content: 运势内容
    :param rank: 运势等级

    :return: 图片，标题，内容，运势等级
    """
    if theme == 'random' or theme not in _themes:
        theme = random.choice(list(_themes.keys()))
    # c选择运势内容
    copywriting = random.choice(_copywriting)
    title = title if title else copywriting['good-luck']
    rank = rank if rank else copywriting['rank']
    text = content if content else random.choice(copywriting['content'])

    # 选择背景图
    base_image_path = _get_random_base_image(theme).relative_to(_fortune_assets_path)

    # 生成 html
    with open(_fortune_assets_path / 'template.html', 'r') as f:
        raw_content = f.read()
    raw_content = raw_content \
        .replace('{image_path}', str(base_image_path).replace('\\', '/')) \
        .replace('{title}', title) \
        .replace('{content}', text)
    # 生成图片
    bytes_data = await render_html(raw_content, str(_fortune_assets_path), image_type,
                                   viewport={'width': 480, 'height': 480})
    return bytes_data, title, text, rank


def get_themes() -> list[str]:
    return [x[0] for _, x in _themes.items()]


_load_fortune_assets()


async def main():
    with open('test.png', 'wb') as f:
        f.write(base64.b64decode((await generate_fortune())[0]))


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
