from nonebot.adapters import Bot, Event
from nonebot.matcher import current_bot
from . import adapters


class Detector:
    """
    检测适配器类型和特性
    """
    @staticmethod
    def is_onebot_v11(context: Bot | Event | None = None) -> bool:
        """
        检测是否为 OneBot v11 协议

        :param context: Bot | Event | None(自动判断)

        :return: 是否为 OneBot v11 协议
        """
        if context is None:
            context = current_bot.get()
        if adapters.onebot_v11_module:
            return isinstance(context, adapters.onebot_v11_module.Bot) \
                or isinstance(context, adapters.onebot_v11_module.Event)
        return False

    @staticmethod
    def is_onebot_v12(context: Bot | Event | None = None) -> bool:
        """
        检测是否为 OneBot v12 协议

        :param context: Bot | Event | None(自动判断)

        :return: 是否为 OneBot v12 协议
        """
        if context is None:
            context = current_bot.get()
        if adapters.onebot_v12_module:
            return isinstance(context, adapters.onebot_v12_module.Bot) \
                or isinstance(context, adapters.onebot_v12_module.Event)
        return False

    @staticmethod
    def is_mirai2(context: Bot | Event | None = None) -> bool:
        """
        检测是否为 Mirai2 协议

        :param context: Bot | Event | None(自动判断)

        :return: 是否为 Mirai2 协议
        """
        if context is None:
            context = current_bot.get()
        if adapters.mirai2_module:
            return isinstance(context, adapters.mirai2_module.Bot) \
                or isinstance(context, adapters.mirai2_module.Event)
        return False

    @staticmethod
    def is_qqguild(context: Bot | Event | None = None) -> bool:
        """
        检测是否为 QQ 频道协议

        :param context: Bot | Event | None(自动判断)

        :return: 是否为 QQGuild 协议
        """
        if context is None:
            context = current_bot.get()
        if adapters.qq_guild_module:
            return isinstance(context, adapters.qq_guild_module.Bot) \
                or isinstance(context, adapters.qq_guild_module.Event)
        return False

    @staticmethod
    def is_kook(context: Bot | Event | None = None) -> bool:
        """
        检测是否为 Kook 协议

        :param context: Bot | Event | None(自动判断)

        :return: 是否为 Kook 协议
        """
        if context is None:
            context = current_bot.get()
        if adapters.kook_module:
            return isinstance(context, adapters.kook_module.Bot) \
                or isinstance(context, adapters.kook_module.Event)
        return False

    @staticmethod
    def is_console(context: Bot | Event | None = None) -> bool:
        """
        检测是否为 Console 协议

        :param context: Bot | Event | None(自动判断)

        :return: 是否为 Console 协议
        """
        if context is None:
            context = current_bot.get()
        if adapters.console_module:
            return isinstance(context, adapters.console_module.Bot) \
                or isinstance(context, adapters.console_module.Event)
        return False

    @staticmethod
    def is_onebot(context: Bot | Event | None = None) -> bool:
        """
        检测是否为 OneBot 协议

        :param context: Bot | Event | None(自动判断)

        :return: 是否为 OneBot 协议
        """
        if context is None:
            context = current_bot.get()
        return Detector.is_onebot_v11(context) or Detector.is_onebot_v12(context)

    @staticmethod
    def is_qq(context: Bot | Event | None = None) -> bool:
        """
        检测是否为 QQ 协议

        :param context: Bot | Event | None(自动判断)

        :return: 是否为 QQ 协议
        """
        if context is None:
            context = current_bot.get()
        return Detector.is_onebot(context) or Detector.is_mirai2(context)

    @staticmethod
    def can_send_image(context: Bot | Event | None = None) -> bool:
        """
        检测是否可以发送图片

        :param context: Bot | Event | None(自动判断)

        :return: 是否可以发送图片
        """
        if context is None:
            context = current_bot.get()
        if Detector.is_qq(context) or Detector.is_kook(context) or Detector.is_qqguild(context):
            return True
        return False

    @staticmethod
    def can_send_file(context: Bot | Event | None = None) -> bool:
        """
        检测是否可以发送文件

        :param context: Bot | Event | None(自动判断)

        :return: 是否可以发送文件
        """
        if context is None:
            context = current_bot.get()
        if Detector.is_onebot(context) or Detector.is_kook(context):
            return True
        return False
