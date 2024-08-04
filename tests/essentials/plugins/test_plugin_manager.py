from typing import Callable

import pytest
from nonebot import get_adapter
from nonebot.adapters.console import Adapter as ConsoleAdapter
from nonebot.adapters.console import Bot as ConsoleBot
from nonebug import App
from pytest_mock import MockerFixture

from essentials.libraries.model import Platform

TEST_PLUGIN_ID = "TEST_PLUGIN_ID"
TEST_PLATFORM_ID = "TEST_PLATFORM_ID"


def test_plugin_manager_create_tables(db_initialize: Callable) -> None:
    from storage.database import Base
    from essentials.plugins.plugin_manager.data import PluginManagementData

    db_initialize()

    assert PluginManagementData.__tablename__ in Base.metadata.tables


def test_disable_plugin_once(db_initialize: Callable) -> None:
    from essentials.plugins.plugin_manager.plugin_manager import disable_plugin, list_disabled_plugins
    from essentials.plugins.plugin_manager.model import Scope

    db_initialize()

    assert list_disabled_plugins(
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    ) == []

    assert disable_plugin(
        TEST_PLUGIN_ID,
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    )

    assert list_disabled_plugins(
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    ) == [TEST_PLUGIN_ID]


def test_disable_plugin_twice(db_initialize: Callable) -> None:
    from essentials.plugins.plugin_manager.plugin_manager import disable_plugin, list_disabled_plugins
    from essentials.plugins.plugin_manager.model import Scope

    db_initialize()

    assert list_disabled_plugins(
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    ) == []

    assert disable_plugin(
        TEST_PLUGIN_ID,
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    )
    assert list_disabled_plugins(
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    ) == [TEST_PLUGIN_ID]

    assert not disable_plugin(
        TEST_PLUGIN_ID,
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    )
    assert list_disabled_plugins(
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    ) == [TEST_PLUGIN_ID]


def test_enable_plugin_with_disabled_plugin(db_initialize: Callable) -> None:
    from essentials.plugins.plugin_manager.plugin_manager import disable_plugin, enable_plugin, list_disabled_plugins
    from essentials.plugins.plugin_manager.model import Scope

    db_initialize()

    assert list_disabled_plugins(
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    ) == []

    assert disable_plugin(
        TEST_PLUGIN_ID,
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    )
    assert list_disabled_plugins(
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    ) == [TEST_PLUGIN_ID]

    assert enable_plugin(
        TEST_PLUGIN_ID,
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    )
    assert list_disabled_plugins(
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    ) == []


def test_enable_plugin_without_disabled_plugin(db_initialize: Callable) -> None:
    from essentials.plugins.plugin_manager.plugin_manager import enable_plugin, list_disabled_plugins
    from essentials.plugins.plugin_manager.model import Scope

    db_initialize()

    assert list_disabled_plugins(
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    ) == []

    assert not enable_plugin(
        TEST_PLUGIN_ID,
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    )
    assert list_disabled_plugins(
        Scope.PRIVATE_CHAT,
        Platform.Console,
        TEST_PLATFORM_ID
    ) == []


@pytest.mark.asyncio
async def test_list_disable_plugin_with_none_in_chat(
        app: App, db_initialize: Callable, make_event: Callable
) -> None:
    from essentials.plugins.plugin_manager import _plugin_manager_command

    db_initialize()

    async with app.test_matcher(_plugin_manager_command) as ctx:
        bot = ctx.create_bot(base=ConsoleBot, adapter=get_adapter(ConsoleAdapter))
        event = make_event("plugin list-disable")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "没有被禁用的插件")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_list_disable_plugin_with_one_in_chat(
        app: App, db_initialize: Callable, make_event: Callable
) -> None:
    from essentials.plugins.plugin_manager import _plugin_manager_command

    db_initialize()

    async with app.test_matcher(_plugin_manager_command) as ctx:
        bot = ctx.create_bot(base=ConsoleBot, adapter=get_adapter(ConsoleAdapter))
        event = make_event(f"plugin disable {TEST_PLUGIN_ID}")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, f"已禁用 {TEST_PLUGIN_ID}")
        ctx.should_finished()

        event = make_event("plugin list-disable")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, f"被禁用的插件:\n{TEST_PLUGIN_ID}")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_disable_plugin_once_in_chat(
    app: App, db_initialize: Callable, make_event: Callable
) -> None:
    from essentials.plugins.plugin_manager import _plugin_manager_command

    db_initialize()

    async with app.test_matcher(_plugin_manager_command) as ctx:
        bot = ctx.create_bot(base=ConsoleBot, adapter=get_adapter(ConsoleAdapter))
        event = make_event(f"plugin disable {TEST_PLUGIN_ID}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, f"已禁用 {TEST_PLUGIN_ID}")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_disable_plugin_twice_in_chat(
        app: App, db_initialize: Callable, make_event: Callable
) -> None:
    from essentials.plugins.plugin_manager import _plugin_manager_command

    db_initialize()

    async with app.test_matcher(_plugin_manager_command) as ctx:
        bot = ctx.create_bot(base=ConsoleBot, adapter=get_adapter(ConsoleAdapter))
        event = make_event(f"plugin disable {TEST_PLUGIN_ID}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, f"已禁用 {TEST_PLUGIN_ID}")
        ctx.should_finished()

        event = make_event(f"plugin disable {TEST_PLUGIN_ID}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, f"{TEST_PLUGIN_ID} 未被启用")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_list_enable_plugin_once_in_chat(
        app: App, db_initialize: Callable, make_event: Callable
) -> None:
    from essentials.plugins.plugin_manager import _plugin_manager_command

    db_initialize()

    async with app.test_matcher(_plugin_manager_command) as ctx:
        bot = ctx.create_bot(base=ConsoleBot, adapter=get_adapter(ConsoleAdapter))
        event = make_event(f"plugin disable {TEST_PLUGIN_ID}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, f"已禁用 {TEST_PLUGIN_ID}")
        ctx.should_finished()

        event = make_event("plugin list-disable")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, f"被禁用的插件:\n{TEST_PLUGIN_ID}")
        ctx.should_finished()

        event = make_event(f"plugin enable {TEST_PLUGIN_ID}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, f"已启用 {TEST_PLUGIN_ID}")
        ctx.should_finished()

        event = make_event("plugin list-disable")
        ctx.receive_event(bot, event)
        ctx.should_pass_rule()
        ctx.should_pass_permission()
        ctx.should_call_send(event, "没有被禁用的插件")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_list_enable_plugin_twice_in_chat(
        app: App, db_initialize: Callable, make_event: Callable
) -> None:
    from essentials.plugins.plugin_manager import _plugin_manager_command

    db_initialize()

    async with app.test_matcher(_plugin_manager_command) as ctx:
        bot = ctx.create_bot(base=ConsoleBot, adapter=get_adapter(ConsoleAdapter))
        event = make_event(f"plugin disable {TEST_PLUGIN_ID}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, f"已禁用 {TEST_PLUGIN_ID}")
        ctx.should_finished()

        event = make_event(f"plugin enable {TEST_PLUGIN_ID}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, f"已启用 {TEST_PLUGIN_ID}")
        ctx.should_finished()

        event = make_event(f"plugin enable {TEST_PLUGIN_ID}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, f"{TEST_PLUGIN_ID} 未被禁用")
        ctx.should_finished()


@pytest.mark.asyncio
async def test_disable_plugin_manager_in_chat(
        app: App, db_initialize: Callable, make_event: Callable
) -> None:
    from essentials.plugins.plugin_manager import _plugin_manager_command, SELF_ID

    db_initialize()

    async with app.test_matcher(_plugin_manager_command) as ctx:
        bot = ctx.create_bot(base=ConsoleBot, adapter=get_adapter(ConsoleAdapter))
        event = make_event(f"plugin disable {SELF_ID}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "不能禁用插件管理器")
        ctx.should_finished()


@pytest.mark.skip("影响后续测试")
@pytest.mark.asyncio
async def test_disable_all_plugin_in_chat(
        app: App, db_initialize: Callable, make_event: Callable
) -> None:
    from essentials.plugins.plugin_manager.model import ALL_PLUGINS
    from essentials.plugins.plugin_manager import _plugin_manager_command

    db_initialize()

    async with app.test_matcher(_plugin_manager_command) as ctx:
        bot = ctx.create_bot(base=ConsoleBot, adapter=get_adapter(ConsoleAdapter))
        event = make_event(f"plugin disable {ALL_PLUGINS}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "已禁用 所有插件")
        ctx.should_finished()

        # 恢复启用，避免影响后续测试
        event = make_event(f"plugin enable {ALL_PLUGINS}")
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "已启用 所有插件")
        ctx.should_finished()
