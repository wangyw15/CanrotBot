from typing import Any

from nonebot import get_driver
from pydantic import BaseModel


class CanrotConfig(BaseModel):
    canrot_enable: bool = True  # always enable aio
    canrot_proxy: str = ''  # starts with http or https
    canrot_data_path: str = './canrot_data'
    canrot_disabled_plugins: list[str] = []


_driver = get_driver()
_global_config = _driver.config
canrot_config = CanrotConfig.parse_obj(_global_config)


def get_config(name: str) -> Any:
    return _global_config.dict()[name]
