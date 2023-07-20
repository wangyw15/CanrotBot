import nonebot
from nonebot.message import event_preprocessor

from . import adapters
from .detector import Detector
from .message import Message, MessageSegment, MessageSegmentTypes

# 动态加载支持并且已安装的适配器
driver = nonebot.get_driver()

for adapter_name in dir(adapters.SupportedAdapters):
    if not adapter_name.startswith('__') and hasattr(getattr(adapters.SupportedAdapters, adapter_name), 'Adapter'):
        try:
            driver.register_adapter(getattr(adapters.SupportedAdapters, adapter_name).Adapter)
            nonebot.logger.info('加载适配器: ' + adapter_name)
        except Exception as e:
            nonebot.logger.info(f'加载 {adapter_name} 失败: {e}')

__all__ = ['adapters',
           'Detector',
           'MessageSegmentTypes',
           'MessageSegment',
           'Message'
           ]
