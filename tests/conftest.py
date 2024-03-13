import nonebot
import pytest
from nonebot.adapters.console import Adapter as ConsoleAdapter


@pytest.fixture(scope="session", autouse=True)
def load_bot():
    # 加载适配器
    driver = nonebot.get_driver()
    driver.register_adapter(ConsoleAdapter)
