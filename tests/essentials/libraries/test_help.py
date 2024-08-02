import pytest
from pytest_mock import MockerFixture


def test_get_plugins_metadata() -> None:
    from essentials.libraries.help import get_plugins_metadata

    assert len(get_plugins_metadata()) > 0


def test_generate_help_text() -> None:
    from essentials.libraries.help import generate_help_text

    assert generate_help_text() != ""


@pytest.mark.asyncio
async def test_generate_help_image(mocker: MockerFixture) -> None:
    from essentials.libraries.help import generate_help_image

    mocker.patch("essentials.libraries.render_by_browser.render_html", return_value=b"TEST")
    assert await generate_help_image() == b"TEST"
