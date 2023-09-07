import typing

from nonebot import on_command, on_regex
from nonebot.adapters import Message
from nonebot.params import CommandArg, RegexGroup
from nonebot.plugin import PluginMetadata

from adapters import unified
from . import xdnmb

__plugin_meta__ = PluginMetadata(
    name='xdnmb',
    description='自动获取串号内容',
    usage='发送链接或者/xd <串号>',
    config=None
)


async def _generate_message(thread_number: str) -> unified.Message | None:
    if data := await xdnmb.get_thread_data(thread_number):
        msg = unified.Message()
        msg.append(data['user_hash'] + ' ' + data['now'] + ' ' + str(data['ReplyCount']) + '条回复\n')
        if data['title'] and data['title'] != '无标题':
            msg.append('标题: ' + data['title'] + '\n')
        msg.append(data['content'] + '\n')
        if data['img']:
            msg.append(unified.MessageSegment.image(f'https://image.nmb.best/image/{data["img"]}{data["ext"]}'))
        return msg
    return None


_thread_number_handler = on_command('xd', aliases={'串', '串号'}, block=True)
_xd_link_handler = on_regex(r'(?:https?:\/\/)?(?:www\.)?nmbxd.com\/t\/(\d+)', block=True)


@_thread_number_handler.handle()
async def _(args: Message = CommandArg()):
    if thread_number := args.extract_plain_text():
        if thread_number.isdigit():
            if msg := await _generate_message(thread_number):
                await msg.send()
                await _thread_number_handler.finish()
    await _thread_number_handler.finish('未找到该串号')


@_xd_link_handler.handle()
async def _(reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]):
    if msg := await _generate_message(reg[0]):
        await msg.send()
        await _thread_number_handler.finish()
    await _thread_number_handler.finish('未找到该串号')
