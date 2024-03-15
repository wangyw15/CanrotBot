import pytest
from nonebug import App
from tests.utils import make_event


@pytest.mark.asyncio
async def test_calculator_matched(app: App):
    from plugins.calculator import calculator_matcher

    async with app.test_matcher(calculator_matcher) as ctx:
        bot = ctx.create_bot()
        event = make_event("2*(6+9)/3=")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "2*(6+9)/3=10")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_calculator_unmatched(app: App):
    from plugins.calculator import calculator_matcher

    async with app.test_matcher(calculator_matcher) as ctx:
        bot = ctx.create_bot()
        event = make_event("2*(6+9)/3")
        ctx.receive_event(bot, event)
        ctx.should_not_pass_rule()

    async with app.test_matcher(calculator_matcher) as ctx:
        bot = ctx.create_bot()
        event = make_event("some message=")
        ctx.receive_event(bot, event)
        ctx.should_not_pass_rule()
