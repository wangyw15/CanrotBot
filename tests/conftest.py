import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

import nonebot
import pytest
from nonebot.adapters.console import Adapter as ConsoleAdapter
from nonebot.adapters.console import Bot as ConsoleBot
from nonebot.adapters.console import Message, MessageEvent
from nonebug.mixin.process import MatcherContext
from nonechat.info import User
from pytest_mock import MockerFixture
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import close_all_sessions

sys.path.append(str(Path(__file__).parent.parent))


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--test-network",
        action="store_true",
        default=False,
        help="Run tests that need network connection"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "network: marks tests as needs network connection")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    if config.getoption("--test-network"):
        return
    skip_network = pytest.mark.skip(reason="need --test-network option to run")
    for item in items:
        if "network" in item.keywords:
            item.add_marker(skip_network)


@pytest.fixture(scope="session", autouse=True)
def db_engine() -> None:
    engine = create_engine("sqlite:///:memory:")
    yield engine
    close_all_sessions()


@pytest.fixture(scope="function", autouse=True)
def db_mock(mocker: MockerFixture, db_engine: Engine) -> None:
    session = sessionmaker(bind=db_engine)

    mocker.patch("storage.database.get_engine", return_value=db_engine)
    mocker.patch("storage.database.get_session", return_value=session)


@pytest.fixture(scope="function")
def db_initialize(db_engine: Engine) -> Callable:
    def _initialize():
        from storage.database import Base
        Base.metadata.drop_all(db_engine)
        Base.metadata.create_all(db_engine)

    return _initialize


@pytest.fixture(scope="session", autouse=True)
def load_bot():
    # 加载适配器
    driver = nonebot.get_driver()
    driver.register_adapter(ConsoleAdapter)

    nonebot.load_plugin("nonebot_plugin_alconna")


@pytest.fixture(scope="session")
def create_event() -> Callable:
    def _create_event(message: str = "",
                      self_id: str = "test",
                      user_id: str = "123456789"):
        return MessageEvent(
            time=datetime.now(),
            self_id=self_id,
            message=Message(message),
            user=User(id=user_id, nickname=user_id)
        )
    return _create_event


@pytest.fixture(scope="session")
def create_bot() -> Callable:
    def _create_bot(context: MatcherContext):
        return context.create_bot(base=ConsoleBot, adapter=nonebot.get_adapter(ConsoleAdapter))
    return _create_bot
