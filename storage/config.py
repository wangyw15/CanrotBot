from nonebot import get_plugin_config
from pydantic import BaseModel


class CanrotConfig(BaseModel):
    canrot_data_path: str = "./canrot_data"
    canrot_database: str = (
        f"sqlite:///{canrot_data_path}/data.db?check_same_thread=False"
    )
    canrot_disabled_plugins: list[str] = []  # TODO 实现禁用插件
    canrot_enabled_adapters: list[str] = ["console"]  # 启用的适配器


canrot_config: CanrotConfig = get_plugin_config(CanrotConfig)
