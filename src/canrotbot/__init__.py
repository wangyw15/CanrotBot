import importlib
from datetime import datetime
from pathlib import Path

import nonebot
from nonebot import logger
from nonebot.log import default_format


def load_plugins(
    ignore_plugin_list: bool = False,
    create_tables: bool = True,
):
    from canrotbot.essentials.libraries import config, database
    from canrotbot.essentials.libraries.model import PluginListMode

    # 内置插件
    nonebot.load_builtin_plugins("echo")

    # 前置插件
    nonebot.load_plugin("nonebot_plugin_apscheduler")
    nonebot.load_plugin("nonebot_plugin_alconna")

    # 基础插件
    essentials_plugins_path = (Path(__file__).parent / "essentials" / "plugins")
    for plugin_path in essentials_plugins_path.iterdir():
        plugin_name = plugin_path.stem

        # 跳过隐藏文件
        if plugin_name.startswith("_"):
            continue

        # 加载插件
        nonebot.load_plugin(f"canrotbot.essentials.plugins.{plugin_name}")

    if create_tables:
        database.create_all_tables()

    # 按需加载普通插件
    plugins_path = Path(__file__).parent / "plugins"
    for plugin_path in plugins_path.iterdir():
        plugin_name = plugin_path.stem

        # 跳过隐藏文件
        if plugin_name.startswith("_"):
            continue

        # 跳过黑名单插件
        if (not ignore_plugin_list) and config.global_config.plugin_list_mode == PluginListMode.Blacklist:
            if plugin_name in config.global_config.plugin_list:
                logger.info(f"Skip loading plugin {plugin_name}")
                continue

        # 跳过非白名单插件
        if (not ignore_plugin_list) and config.global_config.plugin_list_mode == PluginListMode.Whitelist:
            if plugin_name not in config.global_config.plugin_list:
                logger.info(f"Skip loading plugin {plugin_name}")
                continue

        # 加载插件
        nonebot.load_plugin(f"canrotbot.plugins.{plugin_name}")

    if create_tables:
        database.create_all_tables()


def run() -> None:
    from canrotbot.essentials.libraries.model import PluginListMode

    # 初始化
    nonebot.init(alconna_use_command_start=True)
    driver = nonebot.get_driver()

    # 保存日志
    from canrotbot.essentials.libraries import config, database

    logger_path = Path(config.global_config.user_data_path) / "log"
    if not logger_path.exists():
        logger_path.mkdir(parents=True)
    logger.add(
        logger_path / (datetime.now().strftime("%Y-%m-%dT%H%M%S") + ".log"),
        level="WARNING",
        format=default_format,
        rotation="1 week",
    )

    # 注册适配器
    for adapter_name in config.global_config.enabled_adapters:
        adapter_fullname = f"nonebot.adapters.{adapter_name}"
        try:
            adapter_module = importlib.import_module(adapter_fullname)
            driver.register_adapter(adapter_module.Adapter)
        except ModuleNotFoundError as e:
            logger.error(f"Adapter {adapter_fullname} not found")
            logger.exception(e)
        except AttributeError as e:
            logger.error(f"Cannot find Adapter in {adapter_fullname}")
            logger.exception(e)
        except Exception as e:
            logger.error(
                f"Unknown error occurred while registering adapter {adapter_fullname}"
            )
            logger.exception(e)

    load_plugins()

    nonebot.run()
