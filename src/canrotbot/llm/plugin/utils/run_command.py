from nonebot.matcher import current_bot, current_event
from nonebot_plugin_alconna import UniMessage

from ...tools import register_tool


@register_tool()
async def run_command(command: str):
    """
    通过给定的命令来调用机器人所提供的插件功能，注意：插件功能不是tool calling，插件功能只能通过命令调用
    
    Args:
        command: 字符串类型的命令
    """
    bot = current_bot.get()
    event = current_event.get()

    message_attrs = ["message", "_message"]

    for attr in message_attrs:
        if hasattr(event, attr):
            setattr(event, attr, await UniMessage.text(command).export(bot=bot))

    await bot.handle_event(event)  # type: ignore
