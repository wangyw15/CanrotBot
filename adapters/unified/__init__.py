import nonebot
from nonebot.adapters import Bot, Event
from nonebot.message import event_preprocessor

from essentials.libraries import config
from . import adapters
from .detector import Detector
from .message import Message, MessageSegment, MessageSegmentTypes

# 动态加载支持并且已安装的适配器
driver = nonebot.get_driver()

for name, key in adapters.SupportedAdapters.items():
    if not name.startswith('__') \
            and name not in config.canrot_config.canrot_disabled_adapters \
            and key not in config.canrot_config.canrot_disabled_adapters \
            and hasattr(getattr(adapters, key + '_module'), 'Adapter'):
        try:
            driver.register_adapter(getattr(adapters, key + '_module').Adapter)
            nonebot.logger.info('加载适配器: ' + name)
        except Exception as e:
            nonebot.logger.info(f'加载 {name} 失败: {e}')


# @event_preprocessor
# async def _(event: Event, bot: Bot):
#     adapter = adapters.get_adapter(bot)
#     event.message = await adapter.parse_message(event.message)


# 导出名称
__all__ = ['adapters',
           'Detector',
           'MessageSegmentTypes',
           'MessageSegment',
           'Message'
           ]
