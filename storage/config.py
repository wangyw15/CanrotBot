from nonebot import get_plugin_config
from pydantic import BaseModel, Field


class GlobalConfig(BaseModel):
    data_path: str = Field(default="./canrot_data", alias="canrot_data_path")
    disabled_plugins: list[str] = Field(
        default=[], alias="canrot_disabled_plugins"
    )  # TODO 实现禁用插件
    enabled_adapters: list[str] = Field(
        default=["console"], alias="canrot_enabled_adapters"
    )  # 启用的适配器


global_config: GlobalConfig = get_plugin_config(GlobalConfig)
