import sys
from pathlib import Path

import nonebot
import pytest
from nonebot.adapters.console import Adapter as ConsoleAdapter

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
def load_bot():
    # 加载适配器
    driver = nonebot.get_driver()
    driver.register_adapter(ConsoleAdapter)
