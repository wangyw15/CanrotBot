from nonebot.adapters import Bot, Event
from .adapters import Adapters


class Detector:
    """
    检测适配器类型和特性
    """
    @staticmethod
    def is_onebot_v11(context: Bot | Event) -> bool:
        if Adapters.ONEBOT_V11.value:
            return isinstance(context, Adapters.ONEBOT_V11.value.Bot) \
                or isinstance(context, Adapters.ONEBOT_V11.value.Event)
        return False

    @staticmethod
    def is_onebot_v12(context: Bot | Event) -> bool:
        if Adapters.ONEBOT_V12.value:
            return isinstance(context, Adapters.ONEBOT_V12.value.Bot) \
                or isinstance(context, Adapters.ONEBOT_V12.value.Event)
        return False

    @staticmethod
    def is_mirai2(context: Bot | Event) -> bool:
        if Adapters.MIRAI2.value:
            return isinstance(context, Adapters.MIRAI2.value.Bot) \
                or isinstance(context, Adapters.MIRAI2.value.Event)
        return False

    @staticmethod
    def is_qqguild(context: Bot | Event) -> bool:
        if Adapters.QQGUILD.value:
            return isinstance(context, Adapters.QQGUILD.value.Bot) \
                or isinstance(context, Adapters.QQGUILD.value.Event)
        return False

    @staticmethod
    def is_kook(context: Bot | Event) -> bool:
        if Adapters.KOOK.value:
            return isinstance(context, Adapters.KOOK.value.Bot) \
                or isinstance(context, Adapters.KOOK.value.Event)
        return False

    @staticmethod
    def is_console(context: Bot | Event) -> bool:
        if Adapters.CONSOLE.value:
            return isinstance(context, Adapters.CONSOLE.value.Bot) \
                or isinstance(context, Adapters.CONSOLE.value.Event)
        return False

    @staticmethod
    def is_onebot(context: Bot | Event) -> bool:
        return Detector.is_onebot_v11(context) or Detector.is_onebot_v12(context)

    @staticmethod
    def is_qq(context: Bot | Event) -> bool:
        return Detector.is_onebot(context) or Detector.is_mirai2(context) or Detector.is_qqguild(context)

    @staticmethod
    def can_send_image(context: Bot | Event) -> bool:
        """检测是否可以发送图片"""
        if Detector.is_onebot(context) or Detector.is_kook(context) or Detector.is_qqguild(context):
            return True
        return False
