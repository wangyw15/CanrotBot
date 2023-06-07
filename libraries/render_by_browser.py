from pathlib import Path
from typing import Literal

from nonebot import logger, get_driver
from playwright.async_api import Browser, Playwright, async_playwright, Page

_playwright: Playwright | None = None
_browser: Browser | None = None


async def initialize() -> None:
    global _playwright
    global _browser
    if not _playwright:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch()
        logger.info('Initialized browser renderer')


async def get_new_page(**kwargs) -> Page:
    await initialize()
    global _browser
    page = await _browser.new_page(**kwargs)
    return page


async def render_html(html: str, base_path: str | Path, image_type: Literal['png', 'jpeg'] = 'png', **kwargs) -> bytes:
    page = await get_new_page(**kwargs)
    await page.goto(f'file://{base_path}', wait_until='networkidle')
    await page.set_content(html)
    result = await page.screenshot(type=image_type)
    await page.close()
    return result


@get_driver().on_shutdown
async def close_browser():
    global _browser
    global _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
    logger.info('Closed browser renderer')

__all__ = ['get_new_page', 'render_html']
