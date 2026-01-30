import random
from typing import Callable, Literal

from nonebot import get_driver, logger

from canrotbot.essentials.libraries import file, path, render_by_browser

from . import themes

ASSET_PATH = path.get_asset_path("fortune")
asset_version: str = ""
copywriting: list[dict] = []
_themes: dict[str, dict] = {}


@get_driver().on_startup
async def _load_fortune_assets() -> None:
    global asset_version
    global copywriting

    if not asset_version or not copywriting:
        data = file.read_json(ASSET_PATH / "fortune_data.json")
        asset_version = str(data["version"])
        logger.info(f"Fortune version: {asset_version}")
        copywriting = data["copywriting"]
        logger.info(f"Fortune copywriting: {len(copywriting)}")

    themes.load_themes()


def register_theme(
    name: str, html_generator: Callable, aliases: list[str] | None = None
) -> None:
    """
    注册主题

    :param name: 主题名称
    :param html_generator: html 生成函数
    :param aliases: 主题别名
    """
    global _themes
    _themes[name] = {"generator": html_generator, "aliases": aliases or []}


def get_theme_by_name(name: str) -> str:
    """
    根据名称获取主题键

    :param name: 主题名称
    :return: 主题键，若不存在则返回空字符串
    """
    name = name.lower()
    for k, v in _themes.items():
        if name == k or name in v["aliases"]:
            return k
    return ""


def get_random_copywrite() -> tuple[str, str]:
    """
    随机生成一条运势

    Returns:
        运势内容，格式为(标题, 内容)
    """
    selected = random.choice(copywriting)
    content = random.choice(selected["content"])
    return (selected["good-luck"], content)


async def generate_image(
    title: str,
    content: str,
    theme: str = "random",
    image_type: Literal["png", "jpeg"] = "png",
) -> bytes:
    """
    生成运势图片

    Args:
        title: 运势类型
        content: 运势内容
        theme: 运势图片主题
        image_type: 图片格式，支持png和jpeg

    Returns:
        bytes格式的图片
    """
    if t := get_theme_by_name(theme):
        # html template
        generated_html: str = await _themes[t]["generator"](title, content)
    else:
        generated_html: str = await random.choice(list(_themes.values()))["generator"](
            title, content
        )

    # 生成图片
    return await render_by_browser.render_html(
        generated_html,
        str(ASSET_PATH / "template"),
        viewport={"width": 480, "height": 480},
        image_type=image_type,
    )


def get_themes() -> list[str]:
    return list(_themes.keys())
