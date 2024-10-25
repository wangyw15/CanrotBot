from nonebot import get_plugin_config
from pydantic import BaseModel, Field

from .model import PluginListMode


class GlobalConfig(BaseModel):
    user_data_path: str = Field(default="./canrot_data", alias="canrot_user_data_path")
    enabled_adapters: list[str] = Field(
        default=["console"], alias="canrot_enabled_adapters"
    )  # 启用的适配器
    plugin_list_mode: PluginListMode = Field(
        default=PluginListMode.Blacklist, alias="canrot_plugin_list_mode"
    )
    plugin_list: list[str] = Field(default=[""], alias="canrot_plugin_list")


global_config: GlobalConfig = get_plugin_config(GlobalConfig)
