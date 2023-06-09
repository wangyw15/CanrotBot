from nonebot.adapters import Bot, Event
from . import adapters


class Detector:
    """
    检测适配器类型和特性
    """
    @staticmethod
    def is_onebot_v11(context: Bot | Event) -> bool:
        """
        检测是否为 OneBot v11 协议

        :param context: Bot | Event

        :return: 是否为 OneBot v11 协议
        """
        if adapters.onebot_v11:
            return isinstance(context, adapters.onebot_v11.Bot) \
                or isinstance(context, adapters.onebot_v11.Event)
        return False

    @staticmethod
    def is_onebot_v12(context: Bot | Event) -> bool:
        """
        检测是否为 OneBot v12 协议

        :param context: Bot | Event

        :return: 是否为 OneBot v12 协议
        """
        if adapters.onebot_v12:
            return isinstance(context, adapters.onebot_v12.Bot) \
                or isinstance(context, adapters.onebot_v12.Event)
        return False

    @staticmethod
    def is_mirai2(context: Bot | Event) -> bool:
        """
        检测是否为 Mirai2 协议

        :param context: Bot | Event

        :return: 是否为 Mirai2 协议
        """
        if adapters.mirai2:
            return isinstance(context, adapters.mirai2.Bot) \
                or isinstance(context, adapters.mirai2.Event)
        return False

    @staticmethod
    def is_qqguild(context: Bot | Event) -> bool:
        """
        检测是否为 QQ 频道协议

        :param context: Bot | Event

        :return: 是否为 QQGuild 协议
        """
        if adapters.qqguild:
            return isinstance(context, adapters.qqguild.Bot) \
                or isinstance(context, adapters.qqguild.Event)
        return False

    @staticmethod
    def is_kook(context: Bot | Event) -> bool:
        """
        检测是否为 Kook 协议

        :param context: Bot | Event

        :return: 是否为 Kook 协议
        """
        if adapters.kook:
            return isinstance(context, adapters.kook.Bot) \
                or isinstance(context, adapters.kook.Event)
        return False

    @staticmethod
    def is_console(context: Bot | Event) -> bool:
        """
        检测是否为 Console 协议

        :param context: Bot | Event

        :return: 是否为 Console 协议
        """
        if adapters.console:
            return isinstance(context, adapters.console.Bot) \
                or isinstance(context, adapters.console.Event)
        return False

    @staticmethod
    def is_onebot(context: Bot | Event) -> bool:
        """
        检测是否为 OneBot 协议

        :param context: Bot | Event

        :return: 是否为 OneBot 协议
        """
        return Detector.is_onebot_v11(context) or Detector.is_onebot_v12(context)

    @staticmethod
    def is_qq(context: Bot | Event) -> bool:
        """
        检测是否为 QQ 协议

        :param context: Bot | Event

        :return: 是否为 QQ 协议
        """
        return Detector.is_onebot(context) or Detector.is_mirai2(context)

    @staticmethod
    def can_send_image(context: Bot | Event) -> bool:
        """
        检测是否可以发送图片

        :param context: Bot | Event

        :return: 是否可以发送图片
        """
        if Detector.is_qq(context) or Detector.is_kook(context) or Detector.is_qqguild(context):
            return True
        return False

    @staticmethod
    def can_send_file(context: Bot | Event) -> bool:
        """
        检测是否可以发送文件

        :param context: Bot | Event

        :return: 是否可以发送文件
        """
        if Detector.is_onebot(context) or Detector.is_kook(context):
            return True
        return False
