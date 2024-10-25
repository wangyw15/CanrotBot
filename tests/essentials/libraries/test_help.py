import pytest
from pytest_mock import MockerFixture


def test_get_plugins_metadata() -> None:
    from canrotbot.essentials.libraries.help import get_plugins_metadata

    assert len(get_plugins_metadata()) > 0


def test_generate_help_text() -> None:
    from canrotbot.essentials.libraries.help import generate_help_text

    assert generate_help_text() != ""


@pytest.mark.asyncio
async def test_generate_help_image(mocker: MockerFixture) -> None:
    from canrotbot.essentials.libraries.help import generate_help_image

    render_html = mocker.async_stub("canrotbot.essentials.libraries.render_by_browser.render_html")
    render_html.return_value = b"TEST"

    mocker.patch("canrotbot.essentials.libraries.render_by_browser.render_html", new=render_html)
    assert await generate_help_image() == b"TEST"

    render_html.assert_called_once()
