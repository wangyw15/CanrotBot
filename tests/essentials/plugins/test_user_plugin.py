from typing import Callable

import pytest
from nonebug import App
from pytest_mock import MockerFixture

TEST_UID = (1 << 62) + 1
TEST_PLATFORM_ID1 = "TEST_PLATFORM_ID1"
TEST_PLATFORM_ID2 = "TEST_PLATFORM_ID2"


@pytest.mark.asyncio
async def test_user_plugin_help(app: App, create_bot: Callable, create_event: Callable):
    from essentials.plugins.user import _user_command, __plugin_meta__

    async with app.test_matcher(_user_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(message="user")

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, __plugin_meta__.usage)
        ctx.should_finished()


@pytest.mark.asyncio
async def test_user_plugin_info_not_registered(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from essentials.plugins.user import _user_command

    async with app.test_matcher(_user_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(message="user info", user_id=TEST_PLATFORM_ID1)

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, f"platform_id: {TEST_PLATFORM_ID1}\n未注册")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_user_plugin_info_registered(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from essentials.plugins.user import _user_command
    from essentials.libraries import user

    db_initialize()

    uid = user.register(TEST_PLATFORM_ID1)

    async with app.test_matcher(_user_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(message="user info", user_id=TEST_PLATFORM_ID1)

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(
            event,
            f"当前 platform_id: {TEST_PLATFORM_ID1}\n"
            f"uid: {uid}\n"
            f"已绑定的 platform_id:\n"
            f"{TEST_PLATFORM_ID1}",
        )
        ctx.should_finished()


@pytest.mark.asyncio
async def test_user_plugin_register_once(
    app: App,
    mocker: MockerFixture,
    db_initialize: Callable,
    create_bot: Callable,
    create_event: Callable,
):
    from essentials.plugins.user import _user_command
    from essentials.libraries import user

    fake_register = mocker.stub("essentials.libraries.user.register")
    fake_register.return_value = TEST_UID

    mocker.patch.object(user, "register", new=fake_register)

    db_initialize()

    async with app.test_matcher(_user_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(message="user register", user_id=TEST_PLATFORM_ID1)

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, f"注册成功，你的 UID 是 {TEST_UID}")
        ctx.should_finished()

    fake_register.assert_called_once_with(TEST_PLATFORM_ID1)


@pytest.mark.asyncio
async def test_user_plugin_register_twice(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from essentials.plugins.user import _user_command
    from essentials.libraries import user

    db_initialize()

    user.register(TEST_PLATFORM_ID1)

    async with app.test_matcher(_user_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(message="user register", user_id=TEST_PLATFORM_ID1)

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, f"你已经注册过了")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_user_plugin_bind_once(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from essentials.plugins.user import _user_command
    from essentials.libraries import user

    db_initialize()

    user.register(TEST_PLATFORM_ID1)

    async with app.test_matcher(_user_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(
            message=f"user bind {TEST_PLATFORM_ID2}", user_id=TEST_PLATFORM_ID1
        )

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, f"绑定成功")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_user_plugin_bind_twice(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from essentials.plugins.user import _user_command
    from essentials.libraries import user

    db_initialize()

    uid = user.register(TEST_PLATFORM_ID1)
    user.bind(TEST_PLATFORM_ID2, uid)

    async with app.test_matcher(_user_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(
            message=f"user bind {TEST_PLATFORM_ID2}", user_id=TEST_PLATFORM_ID1
        )

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, f"此 platform_id 已经绑定或注册过了")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_user_plugin_unbind_once(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from essentials.plugins.user import _user_command
    from essentials.libraries import user

    db_initialize()

    uid = user.register(TEST_PLATFORM_ID1)
    user.bind(TEST_PLATFORM_ID2, uid)

    async with app.test_matcher(_user_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(
            message=f"user unbind {TEST_PLATFORM_ID2}", user_id=TEST_PLATFORM_ID1
        )

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, f"解绑成功")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_user_plugin_unbind_twice(
    app: App, db_initialize: Callable, create_bot: Callable, create_event: Callable
):
    from essentials.plugins.user import _user_command
    from essentials.libraries import user

    db_initialize()

    user.register(TEST_PLATFORM_ID1)

    async with app.test_matcher(_user_command) as ctx:
        bot = create_bot(ctx)
        event = create_event(
            message=f"user unbind {TEST_PLATFORM_ID2}", user_id=TEST_PLATFORM_ID1
        )

        ctx.receive_event(bot, event)
        ctx.should_pass_permission()
        ctx.should_pass_rule()
        ctx.should_call_send(event, f"此 platform_id 还未绑定或注册")
        ctx.should_finished()
