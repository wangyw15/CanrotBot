import json
import random
from pathlib import Path
from typing import Callable

from jinja2 import Template
from nonebot import logger

from .. import fortune

_legacy_themes: dict[str, list[str]] = {}


def _load_legacy_themes() -> None:
    global _legacy_themes

    if not _legacy_themes:
        with open(fortune.ASSET_PATH / "themes.json", "r", encoding="utf-8") as f:
            _legacy_themes = json.load(f)
            logger.info(f"Fortune legacy themes: {len(_legacy_themes)}")


def _get_random_base_image(theme: str = "random") -> Path:
    if theme == "random" or theme not in _legacy_themes:
        theme = random.choice(list(_legacy_themes.keys()))
    theme_path = fortune.ASSET_PATH / "image" / theme
    return random.choice(list(theme_path.iterdir()))


def _get_legacy_theme_key_from_name(name: str) -> str:
    name = name.lower()
    for _k, _v in _legacy_themes.items():
        if name == _k or name in _v:
            return _k
    return "random"


def _html_generator(theme: str) -> Callable:
    async def _generate_html(title: str, content: str) -> str:
        # 选择背景图
        image_full_path = _get_random_base_image(theme)
        base_image_path = image_full_path.parent.name + "/" + image_full_path.name

        # 生成 html
        with open(fortune.ASSET_PATH / "template" / "legacy.jinja", "r") as f:
            template: Template = Template(f.read())
        return template.render(
            title=title,
            content=content,
            image=str(base_image_path).replace("\\", "/"),
        )

    return _generate_html


# 加载主题
_load_legacy_themes()
# 注册主题
for k, v in _legacy_themes.items():
    fortune.register_theme(k, _html_generator(k), v)
    logger.info(f"Loaded fortune legacy theme: {k}")
