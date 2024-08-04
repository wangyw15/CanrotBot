from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture


class FakeBrowser:
    def __init__(self) -> None:
        self.new_page = AsyncMock()
        self.close = AsyncMock()


class FakePlaywright:
    class FakeChromium:

        def __init__(self) -> None:
            self.launch = AsyncMock()
            self.launch.return_value = FakeBrowser()

    def __init__(self) -> None:
        self.start = AsyncMock()
        self.start.return_value = self

        self.async_playwright = AsyncMock()
        self.async_playwright.return_value = self

        self.chromium = self.FakeChromium()

        self.stop = AsyncMock()

        self.browser = self.chromium.launch.return_value


class FakePage:
    def __init__(self) -> None:
        self.goto = AsyncMock()
        self.set_content = AsyncMock()
        self.screenshot = AsyncMock()
        self.close = AsyncMock()


@pytest.mark.asyncio
async def test_initialize_for_first_time(mocker: MockerFixture) -> None:
    from essentials.libraries import render_by_browser

    playwright = FakePlaywright()
    mocker.patch(
        "essentials.libraries.render_by_browser.async_playwright",
        return_value=playwright,
    )

    assert render_by_browser._playwright is None
    assert render_by_browser._browser is None

    await render_by_browser.initialize()

    assert render_by_browser._playwright == playwright
    assert render_by_browser._browser == playwright.browser

    playwright.start.assert_called_once()
    playwright.chromium.launch.assert_called_once()


@pytest.mark.asyncio
async def test_initialize_twice(mocker: MockerFixture) -> None:
    from essentials.libraries import render_by_browser

    playwright = FakePlaywright()

    mocker.patch("essentials.libraries.render_by_browser._playwright", new=playwright)
    mocker.patch(
        "essentials.libraries.render_by_browser._browser",
        new=playwright.browser,
    )

    assert render_by_browser._playwright == playwright
    assert render_by_browser._browser == playwright.browser

    await render_by_browser.initialize()

    assert render_by_browser._playwright == playwright
    assert render_by_browser._browser == playwright.browser

    playwright.start.assert_not_called()
    playwright.chromium.launch.assert_not_called()


@pytest.mark.asyncio
async def test_dispose_for_first_time(mocker: MockerFixture) -> None:
    from essentials.libraries import render_by_browser

    playwright = FakePlaywright()

    mocker.patch("essentials.libraries.render_by_browser._playwright", new=playwright)

    assert render_by_browser._playwright == playwright

    await render_by_browser.dispose()
    assert render_by_browser._playwright is None
    playwright.stop.assert_called_once()


@pytest.mark.asyncio
async def test_dispose_twice(mocker: MockerFixture) -> None:
    from essentials.libraries import render_by_browser

    playwright = FakePlaywright()

    mocker.patch("essentials.libraries.render_by_browser._playwright", new=playwright)

    assert render_by_browser._playwright == playwright

    await render_by_browser.dispose()
    assert render_by_browser._playwright is None
    playwright.stop.assert_called_once()

    await render_by_browser.dispose()
    playwright.stop.assert_called_once()


@pytest.mark.asyncio
async def test_new_page_with_default_viewport(mocker: MockerFixture) -> None:
    from essentials.libraries import render_by_browser

    browser = FakeBrowser()
    mocker.patch("essentials.libraries.render_by_browser._browser", new=browser)

    await render_by_browser.new_page()

    browser.new_page.assert_called_once_with(viewport={"width": 1000, "height": 1000})


@pytest.mark.asyncio
async def test_new_page_with_custom_viewport(mocker: MockerFixture) -> None:
    from essentials.libraries import render_by_browser

    browser = FakeBrowser()
    mocker.patch("essentials.libraries.render_by_browser._browser", new=browser)

    assert render_by_browser._browser == browser

    viewport = {"width": 2000, "height": 2000}
    await render_by_browser.new_page(viewport=viewport)

    browser.new_page.assert_called_once_with(viewport=viewport)


@pytest.mark.asyncio
async def test_new_page_without_initialize(mocker: MockerFixture) -> None:
    from essentials.libraries import render_by_browser

    mocker.patch("essentials.libraries.render_by_browser._browser", new=None)

    assert render_by_browser._browser is None

    with pytest.raises(RuntimeError):
        await render_by_browser.new_page()


@pytest.mark.asyncio
async def test_render_html(mocker: MockerFixture) -> None:
    from essentials.libraries import render_by_browser

    page = FakePage()
    page.screenshot.return_value = b"TEST"
    mocker.patch("essentials.libraries.render_by_browser.new_page", return_value=page)

    assert await render_by_browser.render_html("FAKEHTML", base_path="FAKEPATH") == b"TEST"

    page.goto.assert_called_once_with("file://FAKEPATH", wait_until="networkidle")
    page.set_content.assert_called_once_with("FAKEHTML")
    page.screenshot.assert_called_once_with(type="png", full_page=True)
    page.close.assert_called_once()
