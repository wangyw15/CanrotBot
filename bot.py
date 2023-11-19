import nonebot
from pathlib import Path

# 初始化
nonebot.init(alconna_use_command_start=True)
driver = nonebot.get_driver()

# 内置插件
nonebot.load_builtin_plugins('echo', 'single_session')

# 前置插件
nonebot.load_plugin('nonebot_plugin_apscheduler')
nonebot.load_plugin('nonebot_plugin_alconna')

# 基础插件
essentials_plugins_path = (Path(__file__).parent / 'essentials' / 'plugins').resolve()
nonebot.load_plugins(str(essentials_plugins_path))

# 普通插件
plugins_path = (Path(__file__).parent / 'plugins').resolve()
nonebot.load_plugins(str(plugins_path))

if __name__ == '__main__':
    nonebot.run()
