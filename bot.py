# 启用的适配器，名称参照 adapters/unified/adapters.py 文件夹下的名称
ENABLED_ADAPTERS = ['console']

import nonebot

# 初始化
nonebot.init()

# 动态加载adapter
from adapters import unified
driver = nonebot.get_driver()

for adapter in dir(unified.adapters):
    if not adapter.startswith('__') and adapter in ENABLED_ADAPTERS:
        driver.register_adapter(getattr(unified.adapters, adapter).Adapter)
        nonebot.logger.info('Adapter registered: ' + adapter)

# 加载插件
nonebot.load_plugins('essentials/plugins')
nonebot.load_plugins('plugins')

if __name__ == '__main__':
    nonebot.run()

