from typing import Any

from nonebot import get_driver
from pydantic import BaseModel


class CanrotConfig(BaseModel):
    canrot_proxy: str = ""  # 代理连接
    canrot_data_path: str = "./canrot_data"
    canrot_database: str = (
        f"sqlite:///{canrot_data_path}/data.db?check_same_thread=False"
    )
    canrot_disabled_plugins: list[str] = []  # TODO 实现禁用插件
    canrot_disabled_adapters: list[str] = []  # 禁用的适配器


_driver = get_driver()
_global_config = _driver.config
canrot_config: CanrotConfig = CanrotConfig.parse_obj(_global_config)


def get_config(name: str) -> Any | None:
    if name not in _global_config.dict():
        return None
    return _global_config.dict()[name]
