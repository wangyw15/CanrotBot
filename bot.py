import nonebot
from pathlib import Path

# 启用的适配器，名称参照 adapters/unified/adapters.py 文件夹下的名称
ENABLED_ADAPTERS = ['console']

# 初始化
nonebot.init()

# 动态加载adapter
from adapters import unified
from essentials.libraries import config
driver = nonebot.get_driver()

for adapter in dir(unified.adapters):
    if not adapter.startswith('__') and adapter in ENABLED_ADAPTERS:
        driver.register_adapter(getattr(unified.adapters, adapter).Adapter)
        nonebot.logger.info('Adapter registered: ' + adapter)

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
