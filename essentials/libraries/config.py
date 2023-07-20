from typing import Any

from nonebot import get_driver
from pydantic import BaseModel


class CanrotConfig(BaseModel):
    canrot_proxy: str = ''  # 代理连接
    canrot_data_path: str = './canrot_data'
    canrot_disabled_plugins: list[str] = []  # 禁用的插件
    canrot_disabled_adapters: list[str] = []  # 禁用的适配器


_driver = get_driver()
_global_config = _driver.config
canrot_config = CanrotConfig.parse_obj(_global_config)


def get_config(name: str) -> Any:
    return _global_config.dict()[name]
