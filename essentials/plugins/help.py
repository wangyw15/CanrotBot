from nonebot import on_command
from nonebot.adapters import Bot

from adapters import unified
from essentials.libraries import help

plugin_help = on_command('help', aliases={'帮助'}, block=True)


@plugin_help.handle()
async def _(bot: Bot):
    if unified.Detector.can_send_image(bot):
        _, img = await help.generate_help_message()
        await unified.MessageSegment.image(img).send()
        await plugin_help.finish()
    else:
        msg, _ = await help.generate_help_message(False)
        await plugin_help.finish(msg)
