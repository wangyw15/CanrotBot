from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from . import bnhhsh

__plugin_meta__ = PluginMetadata(
    name="不能好好说话",
    description="它和「能不能好好说话？」的区别是它不能好好说话，只会说涩涩的话！",
    usage="/<bnhhsh|不能好好说话> <一串英文字母>",
    config=None,
)


bnhhsh_handler = on_command("bnhhsh", aliases={"不能好好说话"}, block=True)


@bnhhsh_handler.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        await bnhhsh_handler.finish(bnhhsh.generate(msg))
    await bnhhsh_handler.finish("用法: " + __plugin_meta__.usage)
