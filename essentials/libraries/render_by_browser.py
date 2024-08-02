from pathlib import Path
from typing import Literal

from nonebot import logger, get_driver
from playwright.async_api import (
    Browser,
    Playwright,
    async_playwright,
    Page,
    ViewportSize,
)

_playwright: Playwright | None = None
_browser: Browser | None = None


async def initialize() -> None:
    """
    初始化浏览器渲染器
    """
    global _playwright
    global _browser
    if not _playwright:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch()


async def dispose() -> None:
    """
    释放浏览器渲染器
    """
    global _browser
    global _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
    logger.info("Closed browser renderer")


async def new_page(viewport: ViewportSize | None = None, **kwargs) -> Page:
    """
    获取一个新的浏览器页面

    :param viewport: 页面视口大小，默认为 1000x1000

    :return: 浏览器页面
    """
    if viewport is None:
        viewport = {"width": 1000, "height": 1000}

    global _browser
    if not _browser:
        raise RuntimeError("浏览器渲染器未初始化")

    page = await _browser.new_page(viewport=viewport, **kwargs)
    return page


async def render_html(
    html: str,
    base_path: str | Path,
    viewport: ViewportSize | None = None,
    image_type: Literal["png", "jpeg"] = "png",
    full_page: bool = True,
    **kwargs,
) -> bytes:
    """
    使用浏览器渲染 HTML

    :param html: HTML 内容
    :param base_path: HTML 基础路径
    :param viewport: 页面视口大小，默认为 1000x1000
    :param image_type: 图片类型，默认为 PNG
    :param full_page: 是否截取整个页面，默认为 True

    :return: 渲染后的图片
    """
    page = await new_page(viewport=viewport, **kwargs)
    await page.goto(f"file://{base_path}", wait_until="networkidle")
    await page.set_content(html)
    result = await page.screenshot(type=image_type, full_page=full_page)
    await page.close()
    return result


@get_driver().on_startup
async def init_browser():
    await initialize()
    logger.info("Initialized browser renderer")


@get_driver().on_shutdown
async def close_browser():
    await dispose()
    logger.info("Closed browser renderer")


__all__ = ["new_page", "render_html"]
