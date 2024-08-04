from typing import Callable

import pytest
from nonebug import App

HELLO_WORLD_CODE = "++++++++++[>+++++++>++++++++++>+++<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+."


def test__brainfuck_interpreter():
    from plugins.brainfuck import interpreter

    result = interpreter.execute(HELLO_WORLD_CODE)
    assert result == "Hello World!"


@pytest.mark.skip("nonebot-plugin-alconna do not support fake adapter")
@pytest.mark.asyncio
async def test_brainfuck_command(app: App, make_event: Callable):
    from plugins.brainfuck import brainfuck_matcher

    async with app.test_matcher(brainfuck_matcher) as ctx:
        bot = ctx.create_bot()
        event = make_event("/bf " + HELLO_WORLD_CODE)
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "Hello World!")
        ctx.should_finished()
