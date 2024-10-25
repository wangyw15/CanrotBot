from typing import Callable

import pytest
from nonebug import App
from pytest_mock import MockerFixture

TEST_UID = (1 << 62) + 1
TEST_PLATFORM_ID1 = "TEST_PLATFORM_ID1"
TEST_PLATFORM_ID2 = "TEST_PLATFORM_ID2"


@pytest.mark.asyncio
async def test_economy_plugin_help(
    app: App, create_bot: Callable, create_event: Callable
):
    from canrotbot.essentials.plugins.economy import _economy_command, __plugin_meta__

    async with app.test_matcher(_economy_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(message="economy")

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, __plugin_meta__.usage)
        ctx.should_finished()


@pytest.mark.asyncio
async def test_economy_plugin_info_not_registered(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from canrotbot.essentials.plugins.economy import _economy_command

    async with app.test_matcher(_economy_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(message="economy info", user_id=TEST_PLATFORM_ID1)

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, f"platform_id: {TEST_PLATFORM_ID1}\n未注册")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_economy_plugin_info_registered(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from canrotbot.essentials.plugins.economy import _economy_command
    from canrotbot.essentials.libraries import user

    db_initialize()

    uid = user.register(TEST_PLATFORM_ID1)

    async with app.test_matcher(_economy_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(message="economy info", user_id=TEST_PLATFORM_ID1)

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(
            event,
            f"platform_id: {TEST_PLATFORM_ID1}\n"
            f"uid: {uid}\n"
            f"当前余额: 0.0 胡萝卜片\n\n"
            f"最近五条交易记录:",
        )
        ctx.should_finished()


@pytest.mark.asyncio
async def test_economy_plugin_info_registered_with_transactions(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from canrotbot.essentials.plugins.economy import _economy_command
    from canrotbot.essentials.libraries import user, economy

    db_initialize()

    uid = user.register(TEST_PLATFORM_ID1)
    economy.earn(uid, 100.0, "TEST")
    record = economy.get_transactions(uid, 1)[0]

    async with app.test_matcher(_economy_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(message="economy info", user_id=TEST_PLATFORM_ID1)

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(
            event,
            f"platform_id: {TEST_PLATFORM_ID1}\n"
            f"uid: {uid}\n"
            f"当前余额: 100.0 胡萝卜片\n\n"
            f"最近五条交易记录:"
            f"\n时间: {record.time.strftime('%Y-%m-%d %H:%M:%S')}"
            f"\n变动: {record.amount}"
            f"\n余额: {record.balance}"
            f"\n备注: {record.description}"
            f"\n--------------------",
        )
        ctx.should_finished()


@pytest.mark.asyncio
async def test_economy_plugin_transfer_to_not_registered_platform_id(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from canrotbot.essentials.plugins.economy import _economy_command
    from canrotbot.essentials.libraries import user

    db_initialize()

    user.register(TEST_PLATFORM_ID1)

    async with app.test_matcher(_economy_command) as ctx:
        bot = create_bot(ctx)

        event = create_event(
            message=f"economy transfer {TEST_PLATFORM_ID2} 100",
            user_id=TEST_PLATFORM_ID1,
        )
        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, "未找到此用户")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_economy_plugin_transfer_to_not_registered_uid(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from canrotbot.essentials.plugins.economy import _economy_command
    from canrotbot.essentials.libraries import user

    db_initialize()

    user.register(TEST_PLATFORM_ID1)

    async with app.test_matcher(_economy_command) as ctx:
        bot = create_bot(ctx)

        event = create_event(
            message=f"economy transfer {TEST_UID} 100", user_id=TEST_PLATFORM_ID1
        )
        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, "未找到此用户")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_economy_plugin_transfer_success(
    app: App,
    mocker: MockerFixture,
    db_initialize: Callable,
    create_bot: Callable,
    create_event: Callable,
):
    from canrotbot.essentials.plugins.economy import _economy_command
    from canrotbot.essentials.libraries import economy, user

    fake_transfer = mocker.stub("transfer")
    fake_transfer.return_value = True

    mocker.patch.object(economy, "transfer", new=fake_transfer)

    db_initialize()

    uid1 = user.register(TEST_PLATFORM_ID1)
    uid2 = user.register(TEST_PLATFORM_ID2)

    async with app.test_matcher(_economy_command) as ctx:
        bot = create_bot(ctx)

        event = create_event(
            message=f"economy transfer {uid2} 100", user_id=TEST_PLATFORM_ID1
        )
        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, f"向 {uid2} 转账 100.0 个胡萝卜片成功")
        ctx.should_finished()

    fake_transfer.assert_called_once_with(uid1, uid2, 100.0)


@pytest.mark.asyncio
async def test_economy_plugin_transfer_fail(
    app: App,
    mocker: MockerFixture,
    db_initialize: Callable,
    create_bot: Callable,
    create_event: Callable,
):
    from canrotbot.essentials.plugins.economy import _economy_command
    from canrotbot.essentials.libraries import economy, user

    fake_transfer = mocker.stub("transfer")
    fake_transfer.return_value = False

    mocker.patch.object(economy, "transfer", new=fake_transfer)

    db_initialize()

    uid1 = user.register(TEST_PLATFORM_ID1)
    uid2 = user.register(TEST_PLATFORM_ID2)

    async with app.test_matcher(_economy_command) as ctx:
        bot = create_bot(ctx)

        event = create_event(
            message=f"economy transfer {uid2} 100", user_id=TEST_PLATFORM_ID1
        )
        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, f"余额不足，向 {uid2} 转账 100.0 个胡萝卜片失败")
        ctx.should_finished()

    fake_transfer.assert_called_once_with(uid1, uid2, 100.0)
