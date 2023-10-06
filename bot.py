import nonebot
from pathlib import Path

# 初始化
nonebot.init()
driver = nonebot.get_driver()

# 加载适配器
from adapters import unified

# 内置插件
nonebot.load_builtin_plugins('echo', 'single_session')

# 前置插件
nonebot.load_plugin('nonebot_plugin_apscheduler')

# 基础插件
essentials_plugins_path = (Path(__file__).parent / 'essentials' / 'plugins').resolve()
nonebot.load_plugins(str(essentials_plugins_path))

# 普通插件
plugins_path = (Path(__file__).parent / 'plugins').resolve()
nonebot.load_plugins(str(plugins_path))

if __name__ == '__main__':
    nonebot.run()
