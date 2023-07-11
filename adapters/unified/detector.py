from nonebot.adapters import Bot, Event
from . import adapters


class Detector:
    """
    检测适配器类型和特性
    """
    @staticmethod
    def is_onebot_v11(context: Bot | Event) -> bool:
        if adapters.onebot_v11:
            return isinstance(context, adapters.onebot_v11.Bot) \
                or isinstance(context, adapters.onebot_v11.Event)
        return False

    @staticmethod
    def is_onebot_v12(context: Bot | Event) -> bool:
        if adapters.onebot_v12:
            return isinstance(context, adapters.onebot_v12.Bot) \
                or isinstance(context, adapters.onebot_v12.Event)
        return False

    @staticmethod
    def is_mirai2(context: Bot | Event) -> bool:
        if adapters.mirai2:
            return isinstance(context, adapters.mirai2.Bot) \
                or isinstance(context, adapters.mirai2.Event)
        return False

    @staticmethod
    def is_qqguild(context: Bot | Event) -> bool:
        if adapters.qqguild:
            return isinstance(context, adapters.qqguild.Bot) \
                or isinstance(context, adapters.qqguild.Event)
        return False

    @staticmethod
    def is_kook(context: Bot | Event) -> bool:
        if adapters.kook:
            return isinstance(context, adapters.kook.Bot) \
                or isinstance(context, adapters.kook.Event)
        return False

    @staticmethod
    def is_console(context: Bot | Event) -> bool:
        if adapters.console:
            return isinstance(context, adapters.console.Bot) \
                or isinstance(context, adapters.console.Event)
        return False

    @staticmethod
    def is_onebot(context: Bot | Event) -> bool:
        return Detector.is_onebot_v11(context) or Detector.is_onebot_v12(context)

    @staticmethod
    def is_qq(context: Bot | Event) -> bool:
        return Detector.is_onebot(context) or Detector.is_mirai2(context)

    @staticmethod
    def can_send_image(context: Bot | Event) -> bool:
        """检测是否可以发送图片"""
        if Detector.is_qq(context) or Detector.is_kook(context) or Detector.is_qqguild(context):
            return True
        return False
