import nonebot
from pathlib import Path

# 初始化
nonebot.init()
driver = nonebot.get_driver()


# 加载adapter
from adapters import unified
from essentials.libraries import config


nonebot.load_builtin_plugins('echo', 'single_session')
nonebot.load_plugin('nonebot_plugin_apscheduler')



# 基础插件
essentials_plugins_path = (Path(__file__).parent / 'essentials' / 'plugins').resolve()
nonebot.load_plugins(str(essentials_plugins_path))
# 普通插件
plugins_path = (Path(__file__).parent / 'plugins').resolve()
for i in plugins_path.iterdir():
    if not i.stem.startswith('_') and i.stem not in config.canrot_config.canrot_disabled_plugins:
        nonebot.load_plugin('plugins.' + i.stem)

if __name__ == '__main__':
    nonebot.run()
