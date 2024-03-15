import random

import pytest
import pytest_mock
from nonebug import App

from tests.utils import make_event


@pytest.mark.asyncio
async def test_crazy_thursday_matched(app: App, mocker: pytest_mock.MockerFixture):
    from plugins.crazy_thursday import crazy_thursday_matcher, crazy_thursday_posts

    expected_post = random.choice(crazy_thursday_posts)
    assert expected_post
    mocker.patch("random.choice", return_value=expected_post)

    async with app.test_matcher(crazy_thursday_matcher) as ctx:
        bot = ctx.create_bot()
        event = make_event("今天是疯狂星期四")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, expected_post)
        ctx.should_finished()
