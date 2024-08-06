import pytest
from nonebot.matcher import current_bot, current_event
from nonebug import App

from typing import Callable

TEST_UID1 = (1 << 62) + 1
TEST_UID2 = (1 << 62) + 2
TEST_PUID1 = "TEST_PUID1"
TEST_PUID2 = "TEST_PUID2"


def test_snowflake_generate_id() -> None:
    from essentials.libraries.user import snowflake

    assert snowflake.generate_id() > 0


def test_create_user_tables(db_initialize: Callable) -> None:
    from essentials.libraries.database import Base
    from essentials.libraries import user

    db_initialize()

    assert user.data.User.__tablename__ in Base.metadata.tables
    assert user.data.Bind.__tablename__ in Base.metadata.tables


def test_register_with_non_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    assert user.register(TEST_PUID1) > 0


def test_register_with_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    assert user.register(TEST_PUID1) > 0
    assert user.register(TEST_PUID1) == 0


def test_puid_user_exists_with_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    assert user.register(TEST_PUID1) > 0
    assert user.puid_user_exists(TEST_PUID1)


def test_puid_user_exists_with_non_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    assert not user.puid_user_exists(TEST_PUID1)


def test_uid_user_exists_with_existing_uid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    registered_uid = user.register(TEST_PUID1)
    assert registered_uid > 0
    assert user.uid_user_exists(registered_uid)


def test_uid_user_exists_with_non_existing_uid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    assert not user.uid_user_exists(TEST_UID1)


def test_bind_with_existing_uid_and_non_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    registered_uid = user.register(TEST_PUID1)
    assert registered_uid > 0
    assert user.bind(TEST_PUID2, registered_uid)


def test_bind_with_non_existing_uid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    assert not user.bind(TEST_PUID1, TEST_UID1)


def test_bind_with_existing_uid_and_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    registered_uid = user.register(TEST_PUID1)
    assert registered_uid > 0
    assert not user.bind(TEST_PUID1, registered_uid)


def test_unbind_with_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    registered_uid = user.register(TEST_PUID1)
    assert registered_uid > 0
    assert user.bind(TEST_PUID2, registered_uid)
    assert user.unbind(TEST_PUID2)


def test_unbind_with_non_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    assert not user.unbind(TEST_PUID1)


def test_get_uid_with_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    registered_uid = user.register(TEST_PUID1)
    assert registered_uid > 0
    assert user.get_uid(TEST_PUID1) == registered_uid


def test_get_uid_with_non_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    assert user.get_uid(TEST_PUID1) == 0


@pytest.mark.asyncio
async def test_get_uid_with_auto_puid(db_initialize: Callable, create_event: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    registered_uid = user.register(TEST_PUID1)
    assert registered_uid > 0
    current_event.set(create_event(user_id=TEST_PUID1))
    assert user.get_uid() == registered_uid


def test_get_bind_by_uid_with_existing_uid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    registered_uid = user.register(TEST_PUID1)
    assert registered_uid > 0
    assert user.bind(TEST_PUID2, registered_uid)
    assert user.get_bind_by_uid(registered_uid) == [TEST_PUID1, TEST_PUID2]


def test_get_bind_by_uid_with_non_existing_uid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    assert user.get_bind_by_uid(TEST_UID1) == []


def test_get_bind_by_puid_with_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    registered_uid = user.register(TEST_PUID1)
    assert registered_uid > 0
    assert user.bind(TEST_PUID2, registered_uid)
    assert user.get_bind_by_puid(TEST_PUID2) == [TEST_PUID1, TEST_PUID2]


def test_get_bind_by_puid_with_non_bind_puid(db_initialize: Callable) -> None:
    from essentials.libraries import user

    db_initialize()

    assert user.get_bind_by_puid(TEST_PUID1) == []


@pytest.mark.asyncio
async def test_get_user_name_with_default_parameters(
    db_initialize: Callable, app: App, create_event: Callable
) -> None:
    from essentials.libraries import user

    db_initialize()

    async with app.test_matcher() as ctx:
        bot = ctx.create_bot()

        current_bot.set(bot)
        current_event.set(create_event(user_id=TEST_PUID1))

        assert await user.get_user_name() is None


@pytest.mark.asyncio
async def test_get_user_name_with_bot_provided(
    db_initialize: Callable, app: App, create_event: Callable
) -> None:
    from essentials.libraries import user

    db_initialize()

    async with app.test_matcher() as ctx:
        bot = ctx.create_bot()

        current_event.set(create_event(user_id=TEST_PUID1))

        assert await user.get_user_name(bot=bot) is None


@pytest.mark.asyncio
async def test_get_user_name_with_event_provided(
    db_initialize: Callable, app: App, create_event: Callable
) -> None:
    from essentials.libraries import user

    db_initialize()

    async with app.test_matcher() as ctx:
        bot = ctx.create_bot()

        current_bot.set(bot)

        assert await user.get_user_name(event=create_event(user_id=TEST_PUID1)) is None


@pytest.mark.asyncio
async def test_get_user_name_with_bot_and_event_provided(
    db_initialize: Callable, app: App, create_event: Callable
) -> None:
    from essentials.libraries import user

    db_initialize()

    async with app.test_matcher() as ctx:
        bot = ctx.create_bot()

        assert await user.get_user_name(bot=bot, event=create_event(user_id=TEST_PUID1)) is None


# TODO 完善各平台get_user_name测试
