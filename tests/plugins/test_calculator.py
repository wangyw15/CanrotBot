from typing import Callable

import pytest
from nonebug import App


@pytest.mark.asyncio
async def test_calculator_matched(app: App, create_event: Callable):
    from canrotbot.plugins.calculator import calculator_matcher

    async with app.test_matcher(calculator_matcher) as ctx:
        bot = ctx.create_bot()
        event = create_event("2*(6+9)/3=")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "2*(6+9)/3=10")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_calculator_unmatched(app: App, create_event: Callable):
    from canrotbot.plugins.calculator import calculator_matcher

    async with app.test_matcher(calculator_matcher) as ctx:
        bot = ctx.create_bot()
        event = create_event("2*(6+9)/3")
        ctx.receive_event(bot, event)
        ctx.should_not_pass_rule()

    async with app.test_matcher(calculator_matcher) as ctx:
        bot = ctx.create_bot()
        event = create_event("some message=")
        ctx.receive_event(bot, event)
        ctx.should_not_pass_rule()


@pytest.mark.asyncio
async def test_calculator_error(app: App, create_event: Callable):
    from canrotbot.plugins.calculator import calculator_matcher

    async with app.test_matcher(calculator_matcher) as ctx:
        bot = ctx.create_bot()
        event = create_event("1/0=")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "计算错误\ndivision by zero")
        ctx.should_finished()

    async with app.test_matcher(calculator_matcher) as ctx:
        bot = ctx.create_bot()
        event = create_event("1()=")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "计算错误\n'int' object is not callable")
        ctx.should_finished()
