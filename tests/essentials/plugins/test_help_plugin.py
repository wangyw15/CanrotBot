from typing import Callable

import pytest
from nonebug import App
from pytest_mock import MockerFixture


@pytest.mark.asyncio
async def test_help_text(
    app: App,
    mocker: MockerFixture,
    create_bot: Callable,
    create_event: Callable
):
    from essentials.plugins.help import _help_command
    from essentials.libraries import help as help_lib

    fake_generate_help_text = mocker.stub("generate_help_text")
    fake_generate_help_text.return_value = "HELP_MSG"

    mocker.patch.object(
        help_lib,
        "generate_help_text",
        new=fake_generate_help_text
    )

    async with app.test_matcher(_help_command) as ctx:
        bot = create_bot(ctx)
        event = create_event("help")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_call_send(event, fake_generate_help_text.return_value)
        ctx.should_finished()

    fake_generate_help_text.assert_called_once()
