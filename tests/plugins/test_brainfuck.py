from typing import Callable

import pytest
from nonebot import get_adapter
from nonebot.adapters.console import Adapter as ConsoleAdapter
from nonebot.adapters.console import Bot as ConsoleBot
from nonebug import App

HELLO_WORLD_CODE = "++++++++++[>+++++++>++++++++++>+++<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+."


def test__brainfuck_interpreter():
    from plugins.brainfuck import interpreter

    result = interpreter.execute(HELLO_WORLD_CODE)
    assert result == "Hello World!"


@pytest.mark.asyncio
async def test_brainfuck_command(app: App, create_bot: Callable, create_event: Callable):
    from plugins.brainfuck import brainfuck_matcher

    async with app.test_matcher(brainfuck_matcher) as ctx:
        bot = create_bot(ctx)
        event = create_event("bf " + HELLO_WORLD_CODE)
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "Hello World!")
        ctx.should_finished()
