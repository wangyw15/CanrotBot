from typing import Callable

import pytest
from nonebug import App


@pytest.mark.asyncio
async def test_bnhhsh(app: App, create_event: Callable):
    from plugins.bnhhsh import bnhhsh_handler

    async with app.test_matcher(bnhhsh_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("/bnhhsh a")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "俺")
        ctx.should_finished()
