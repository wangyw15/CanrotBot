import random
from typing import Tuple, Literal, Callable

from nonebot import logger

from essentials.libraries import render_by_browser
from storage import asset
from . import themes

fortune_assets = asset.AssetManager("fortune")
_fortune_assets_version: str = ""
_copywriting: list[dict] = []
_themes: dict[str, dict] = {}


def _load_fortune_assets() -> None:
    global _fortune_assets_version
    global _copywriting

    if not _fortune_assets_version or not _copywriting:
        data = fortune_assets["fortune_data"]
        _fortune_assets_version = str(data["version"])
        logger.info(f"Fortune version: {_fortune_assets_version}")
        _copywriting = data["copywriting"]
        logger.info(f"Fortune copywriting: {len(_copywriting)}")

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


async def generate_fortune(
    theme: str = "random",
    image_type: Literal["png", "jpeg"] = "png",
    title: str = "",
    content: str = "",
    rank: int = 0,
) -> Tuple[bytes, str, str, int]:
    """
    生成给定主题的运势图片，如果不给定运势内容则随机选择

    :param theme: 运势主题
    :param image_type: 返回图片格式
    :param title: 运势标题
    :param content: 运势内容
    :param rank: 运势等级

    :return: 图片，标题，内容，运势等级
    """

    # 选择运势内容
    copywriting = random.choice(_copywriting)
    title = title if title else copywriting["good-luck"]
    rank = rank if rank else copywriting["rank"]
    text = content if content else random.choice(copywriting["content"])

    # 新版主题
    if t := get_theme_by_name(theme):
        raw_content: str = await _themes[t]["generator"]()
    else:
        raw_content: str = await random.choice(list(_themes.values()))["generator"]()

    # 生成图片
    raw_content = raw_content.replace("{{title}}", title).replace("{{content}}", text)
    bytes_data = await render_by_browser.render_html(
        raw_content,
        str(fortune_assets / "template"),
        viewport={"width": 480, "height": 480},
        image_type=image_type,
    )
    return bytes_data, title, text, rank


def get_themes() -> list[str]:
    return list(_themes.keys())


_load_fortune_assets()


async def main():
    with open("test.png", "wb") as f:
        f.write((await generate_fortune())[0])


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
