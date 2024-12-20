from typing import Callable

import pytest
from nonebug import App
from pytest_mock import MockerFixture


@pytest.fixture(scope="function", autouse=True)
def setup_currency(mocker: MockerFixture):
    mocker.patch(
        "canrotbot.plugins.currency.fetch_currency",
        return_value=[
            {
                "currencyCHName": "美元",
                "currencyENName": "USD",
                "foreignBuy": "700.00",
                "foreignSell": "700.00",
            },
            {
                "currencyCHName": "日元",
                "currencyENName": "JPY",
                "foreignBuy": "4.5000",
                "foreignSell": "4.5000",
            },
        ]
    )


@pytest.mark.asyncio
async def test_to_cny_with_default_amount(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("usd")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "100.0000美元=700.0000人民币")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_from_cny_with_default_amount(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("100cnyusd")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "100.0000人民币=14.2857美元")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_usd_jpy_with_default_amount(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("100usdjpy")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "100.0000美元=15555.5556日元")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_to_cny_with_custom_amount(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("1usd")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "1.0000美元=7.0000人民币")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_from_cny_with_custom_amount(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("1cnyusd")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "1.0000人民币=0.1429美元")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_usd_jpy_with_custom_amount(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("1usdjpy")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "1.0000美元=155.5556日元")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_invalid_from_currency(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("1aaa")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "未找到货币: aaa")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_invalid_to_currency(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("1usdaaa")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "未找到货币: aaa")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_invalid_all_currency(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("1aaabbb")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "未找到货币: aaa bbb")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_unintended_trigger_with_only_currency_from(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("aaa")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_finished()


@pytest.mark.asyncio
async def test_unintended_trigger_with_both_currency(app: App, create_event: Callable):
    from canrotbot.plugins.currency import currency_convert_handler

    async with app.test_matcher(currency_convert_handler) as ctx:
        bot = ctx.create_bot()
        event = create_event("genius")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_finished()
