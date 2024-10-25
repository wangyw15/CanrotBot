from typing import Callable

import pytest
import pytest_mock
from nonebug import App


@pytest.mark.asyncio
async def test_wordle_success(
    app: App, mocker: pytest_mock.MockerFixture, create_event: Callable
):
    from canrotbot.plugins import wordle

    expected_answer = "hello"
    assert expected_answer
    assert len(expected_answer) == 5
    mocker.patch("random.choice", return_value=expected_answer)

    async with app.test_matcher(wordle.wordle_matcher) as ctx:
        bot = ctx.create_bot()
        event = create_event("/wordle")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "新一轮wordle游戏开始，请输入单词")

        event = create_event("crane")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "crane\n❌❌❌❌❔\n第1次")
        ctx.should_rejected()

        event = create_event("hotel")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "crane\n❌❌❌❌❔\nhotel\n⭕❔❌❔❔\n第2次")
        ctx.should_rejected()

        event = create_event("hello")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "恭喜你猜对了！\n共用了3次机会")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_wordle_invalid_word(
    app: App, mocker: pytest_mock.MockerFixture, create_event: Callable
):
    from canrotbot.plugins import wordle

    expected_answer = "hello"
    assert expected_answer
    assert len(expected_answer) == 5
    mocker.patch("random.choice", return_value=expected_answer)

    async with app.test_matcher(wordle.wordle_matcher) as ctx:
        bot = ctx.create_bot()
        event = create_event("/wordle")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "新一轮wordle游戏开始，请输入单词")

        event = create_event("aaaaa")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "你输入的单词不在词库中")
        ctx.should_rejected()

        event = create_event("hello")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "恭喜你猜对了！\n共用了1次机会")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_wordle_too_many_tries(
    app: App, mocker: pytest_mock.MockerFixture, create_event: Callable
):
    from canrotbot.plugins import wordle

    expected_answer = "hello"
    assert expected_answer
    assert len(expected_answer) == 5
    mocker.patch("random.choice", return_value=expected_answer)

    async with app.test_matcher(wordle.wordle_matcher) as ctx:
        bot = ctx.create_bot()
        event = create_event("/wordle")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "新一轮wordle游戏开始，请输入单词")

        event = create_event("crane")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "crane\n"
                                    "❌❌❌❌❔\n"
                                    "第1次")
        ctx.should_rejected()

        event = create_event("crane")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "第2次")
        ctx.should_rejected()

        event = create_event("crane")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "第3次")
        ctx.should_rejected()

        event = create_event("crane")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "第4次")
        ctx.should_rejected()

        event = create_event("crane")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "第5次")
        ctx.should_rejected()

        event = create_event("crane")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "crane\n"
                                    "❌❌❌❌❔\n"
                                    "第6次\n"
                                    "你已经用完了6次机会\n"
                                    "答案是hello")
        ctx.should_finished()
