from datetime import datetime
from pathlib import Path

import nonebot
import nonebot.adapters.console as console
import nonebot.adapters.kaiheila as kook
import nonebot.adapters.mirai2 as mirai2
import nonebot.adapters.onebot.v11 as onebot_v11
import nonebot.adapters.onebot.v12 as onebot_v12
import nonebot.adapters.qqguild as qqguild
from nonebot import logger
from nonebot.log import default_format

# 初始化
nonebot.init(alconna_use_command_start=True)
driver = nonebot.get_driver()

# 保存日志
from storage import config

logger_path = Path(config.canrot_config.canrot_data_path) / "log"
if not logger_path.exists():
    logger_path.mkdir(parents=True)
logger.add(
    logger_path / (datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log"),
    level="WARNING",
    format=default_format,
    rotation="1 week",
)

# 注册适配器
if "console" not in config.canrot_config.canrot_disabled_adapters:
    driver.register_adapter(console.Adapter)
if "kook" not in config.canrot_config.canrot_disabled_adapters:
    driver.register_adapter(kook.Adapter)
if "mirai2" not in config.canrot_config.canrot_disabled_adapters:
    driver.register_adapter(mirai2.Adapter)
if "onebot_v11" not in config.canrot_config.canrot_disabled_adapters:
    driver.register_adapter(onebot_v11.Adapter)
if "onebot_v12" not in config.canrot_config.canrot_disabled_adapters:
    driver.register_adapter(onebot_v12.Adapter)
if "qqguild" not in config.canrot_config.canrot_disabled_adapters:
    driver.register_adapter(qqguild.Adapter)

# 内置插件
nonebot.load_builtin_plugins("echo", "single_session")

# 前置插件
nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_plugin("nonebot_plugin_alconna")

# 基础插件
essentials_plugins_path = (Path(__file__).parent / "essentials" / "plugins").resolve()
nonebot.load_plugins(str(essentials_plugins_path))

# 普通插件
plugins_path = (Path(__file__).parent / "plugins").resolve()
nonebot.load_plugins(str(plugins_path))

if __name__ == "__main__":
    nonebot.run()
