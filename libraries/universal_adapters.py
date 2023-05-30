import base64
import re
from pathlib import Path

import httpx
from nonebot.adapters import Bot, Event, Message, MessageSegment
from nonebot.permission import Permission

from .config import get_config

# 不同适配器
try:
    import nonebot.adapters.onebot.v11 as ob11
except ModuleNotFoundError:
    ob11 = None
try:
    import nonebot.adapters.onebot.v12 as ob12
except ModuleNotFoundError:
    ob12 = None
try:
    import nonebot.adapters.kaiheila as kook
except ModuleNotFoundError:
    kook = None
try:
    import nonebot.adapters.mirai2 as mirai2
except ModuleNotFoundError:
    mirai2 = None
try:
    import nonebot.adapters.console as console
except ModuleNotFoundError:
    console = None
try:
    import nonebot.adapters.qqguild as qqguild
except ModuleNotFoundError:
    qqguild = None

# permission
GROUP = Permission()
'''Group permission for different adapters'''
if ob11:
    GROUP |= ob11.GROUP
if ob12:
    GROUP |= ob12.GROUP
if mirai2:
    GROUP |= mirai2.GROUP_MEMBER | mirai2.GROUP_ADMINS

GROUP_ADMIN = Permission()
'''Group admin permission for only mirai2 and onebot v11'''
if ob11:
    GROUP_ADMIN |= ob11.GROUP_ADMIN
if mirai2:
    GROUP_ADMIN |= mirai2.GROUP_ADMINS

GROUP_OWNER = Permission()
'''Group owner permission for only mirai2 and onebot v11'''
if ob11:
    GROUP_OWNER |= ob11.GROUP_OWNER
if mirai2:
    GROUP_OWNER |= mirai2.GROUP_OWNER

# split line
MESSAGE_SPLIT_LINE = "--------------------"


def get_group_id(event: Event) -> str | None:
    """从不同的事件中获取群ID"""
    if ob11 and isinstance(event, ob11.GroupMessageEvent) or ob12 and isinstance(event, ob12.GroupMessageEvent):
        return str(event.group_id)
    elif mirai2 and isinstance(event, mirai2.GroupMessage):
        return str(event.sender.group.id)
    elif kook and isinstance(event, kook.event.ChannelMessageEvent):
        return str(event.group_id)
    return None


async def get_user_name(event: Event, bot: Bot, default: str = None) -> str | None:
    """从不同的事件中获取用户昵称"""
    # onebot v11
    if ob11 and isinstance(bot, ob11.Bot):
        if isinstance(event, ob11.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, ob11.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.user_id)
            return user_info['nickname']
    # onebot v12
    elif ob12 and isinstance(bot, ob12.Bot):
        if isinstance(event, ob12.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, ob12.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.user_id)
            return user_info['nickname']
    # mirai2
    elif mirai2 and isinstance(bot, mirai2.Bot):
        if isinstance(event, mirai2.GroupMessage):
            return event.sender.name
        elif isinstance(event, mirai2.FriendMessage):
            return event.sender.nickname
    # kook
    elif kook and isinstance(bot, kook.Bot):
        if isinstance(event, kook.Event) and hasattr(event, 'extra'):
            return event.extra.author.nickname
    return default


async def get_bot_name(event: Event, bot: Bot, default: str = None) -> str | None:
    """从不同的事件中获取机器人昵称"""
    # onebot v11
    if ob11 and isinstance(bot, ob11.Bot):
        if isinstance(event, ob11.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.self_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, ob11.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.self_id)
            return user_info['nickname']
    # onebot v12
    elif ob12 and isinstance(bot, ob12.Bot):
        if isinstance(event, ob12.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.self.user_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, ob12.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.self.user_id)
            return user_info['nickname']
    # mirai2
    elif mirai2 and isinstance(bot, mirai2.Bot):
        if isinstance(event, mirai2.GroupMessage):
            user_info = await bot.member_profile(target=event.sender.group.id, member_id=bot.self_id)
            return user_info['nickname']
        elif isinstance(event, mirai2.FriendMessage):
            user_info = bot.bot_pro_file()
            return user_info['nickname']
    # kook
    elif kook and isinstance(bot, kook.Bot):
        if isinstance(event, kook.Event) and hasattr(event, 'group_id'):
            user_info = await bot.user_view(user_id=bot.self_id, group_id=event.group_id)
            return user_info.nickname
    return default


def generate_onebot_group_forward_message(content: list[str], name: str, sender_id: str) -> list[dict]:
    """生成OneBot群组转发消息"""
    msg_nodes: list[dict] = []
    for msg in content:
        msg_nodes.append({
            'type': 'node',
            'data': {
                'name': name,
                'uin': sender_id,
                'content': msg.strip()
            }
        })
    return msg_nodes


if proxy := get_config('canrot_proxy'):
    _client = httpx.AsyncClient(proxies=proxy)
else:
    _client = httpx.AsyncClient()
_client.timeout = 10


async def fetch_bytes_data(url: str) -> bytes | None:
    """从URL获取bytes数据"""
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        return resp.content
    return None


async def fetch_json_data(url: str) -> dict | None:
    """从URL获取json数据"""
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None


async def send_group_forward_message(content: list[str], bot: Bot, event: Event, default_bot_name: str = 'Canrot',
                                     split: str = MESSAGE_SPLIT_LINE, header: str = '') -> None:
    if is_onebot_v11(bot) or is_onebot_v12(bot):
        if header:
            content.insert(0, header)
        msg_nodes = generate_onebot_group_forward_message(content, await get_bot_name(event, bot, default_bot_name),
                                                          bot.self_id)
        if isinstance(event, ob11.GroupMessageEvent) or isinstance(event, ob12.GroupMessageEvent):
            await bot.send_group_forward_msg(group_id=event.group_id, messages=msg_nodes)
            return
    header = header + '\n\n' if header else ''
    msg = header + ('\n' + split + '\n').join(content)
    if is_onebot_v11(bot):
        await bot.send(event, ob11.Message(msg))
        return
    elif is_onebot_v12(bot):
        await bot.send(event, ob12.Message(msg))
        return
    await bot.send(event, msg)


async def send_image(img: bytes | str | Path, bot: Bot, event: Event) -> bool:
    """
    为不同的适配器发送图片

    :param img: 图片的`bytes`或者本地路径，`str`类型根据适配器不同有不同的含义，在Kook和QQ频道中看作链接
    :param bot: 机器人实例
    :param event: 事件实例
    """
    if is_onebot_v11(bot):
        await bot.send(event, ob11.MessageSegment.image(file=img))
        return True
    elif is_onebot_v12(bot):
        if isinstance(img, bytes):
            b64img = base64.b64encode(img).decode()
            await bot.send(event, ob12.Message(f'[CQ:image,file=base64://{b64img}]'))
        elif isinstance(img, str) or isinstance(img, Path):
            await bot.send(event, ob12.Message(f'[CQ:image,file={img}]'))
        return True
    elif is_kook(bot):
        if isinstance(img, bytes):
            url = await bot.upload_file(img)
        elif isinstance(img, str):
            img_data = await fetch_bytes_data(img)
            if img_data:
                url = await bot.upload_file(img_data)
        elif isinstance(img, Path):
            with open(img, 'rb') as f:
                url = await bot.upload_file(f.read())
        if url:
            await bot.send(event, kook.MessageSegment.image(url))
            return True
    elif is_qqguild(bot):
        if isinstance(img, str):
            await bot.send(event, qqguild.MessageSegment.image(img))
        else:
            await bot.send(event, qqguild.MessageSegment.file_image(img))
        return True
    return False


def can_send_image(bot: Bot) -> bool:
    """检测是否可以发送图片"""
    if is_onebot_v11(bot) or is_onebot_v12(bot) or is_kook(bot) or is_qqguild(bot):
        return True
    return False


async def send_rich_text_message(msg: Message, bot: Bot, event: Event):
    """
    发送富文本消息，目前仅支持纯文字和图片

    消息类型中，`image` 代表图片，`text` 代表文字消息，其余类型会被忽略

    如果是文字消息，则保存在 `content` 键中

    如果是图片消息，`url` 键保存图片链接，`bytes` 键保存二进制图片，`path` 保存本地路径（三选一）

    QQ和QQ频道发送为一条消息，Kook则是图文拆分发送，其余则是忽略图片

    :param msg: 富文本消息
    :param bot: 机器人实例
    :param event: 事件实例
    """
    if is_onebot_v11(bot):
        final_msg = ob11.Message()
        for segment in msg:
            if segment.type == 'image':
                if 'url' in segment.data:
                    final_msg.append(ob11.MessageSegment.image(segment.data['url']))
                elif 'bytes' in segment.data:
                    final_msg.append(ob11.MessageSegment.image(segment.data['bytes']))
                elif 'path' in segment.data:
                    final_msg.append(ob11.MessageSegment.image(segment.data['path']))
            elif segment.type == 'text' or segment.is_text():
                final_msg.append(segment.data['content'])
        await bot.send(event, final_msg)
    elif is_onebot_v12(bot):
        final_msg = ob12.Message()
        for segment in msg:
            if segment.type == 'image':
                if 'url' in segment.data:
                    final_msg.append(f'[CQ:image,file={segment.data["url"]}]')
                elif 'bytes' in segment.data:
                    b64img = base64.b64encode(segment.data['bytes']).decode('utf-8')
                    final_msg.append(f'[CQ:image,file=base64://{b64img}]')
                elif 'path' in segment.data:
                    final_msg.append(f'[CQ:image,file={segment.data["path"]}]')
            elif segment.type == 'text' or segment.is_text():
                final_msg.append(segment.data['content'])
        await bot.send(event, final_msg)
    elif is_kook(bot):
        tmp = ''
        for segment in msg:
            if segment.type == 'image':
                if tmp.strip():
                    await bot.send(event, tmp)
                    tmp = ''
                if 'url' in segment.data:
                    await send_image(segment.data['url'], bot, event)
                elif 'bytes' in segment.data:
                    await send_image(segment.data['bytes'], bot, event)
                elif 'path' in segment.data:
                    await send_image(segment.data['path'], bot, event)
            elif segment.type == 'text' or segment.is_text():
                tmp += segment.data['content']
        if tmp.strip():
            await bot.send(event, tmp)
            tmp = ''
    elif is_qqguild(bot):
        final_msg = qqguild.Message()
        for segment in msg:
            if segment.type == 'image':
                if 'url' in segment.data:
                    final_msg.append(qqguild.MessageSegment.image(segment.data['url']))
                elif 'bytes' in segment.data:
                    final_msg.append(qqguild.MessageSegment.file_image(segment.data['bytes']))
                elif 'path' in segment.data:
                    final_msg.append(qqguild.MessageSegment.file_image(segment.data['path']))
            elif segment.type == 'text' or segment.is_text():
                final_msg.append(segment.data['content'])
        await bot.send(event, final_msg)
    else:
        final_msg = ''
        for segment in msg:
            if segment.type == 'text':
                final_msg += segment.data['content']
        await bot.send(event, final_msg)


def is_url(msg: MessageSegment | str) -> bool:
    """检测是否为URL"""
    if isinstance(msg, str):
        return re.match(r'^https?://', msg) is not None
    elif msg.is_text():
        msg = str(msg)
        return re.match(r'^https?://', msg) is not None
    elif isinstance(msg, kook.MessageSegment):
        if msg.type == 'kmarkdown':
            msg = re.search(r'\[.*]\((\S+)\)', msg.plain_text()).groups()[0]
            return re.match(r'^https?://', msg) is not None
        elif msg.type == 'text':
            return re.match(r'^https?://', msg.plain_text()) is not None
    return False


def seconds_to_time(seconds: float) -> str:
    ms = int(seconds % 1 * 1000)
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}.{str(ms).zfill(3)}"


def get_puid(bot: Bot, event: Event) -> str:
    puid = event.get_user_id()
    if is_onebot_v11(bot) or is_onebot_v12(bot) or is_mirai2(bot):
        puid = 'qq_' + puid
    elif is_kook(bot):
        puid = 'kook_' + puid
    elif is_console(bot):
        puid = 'console_console'
    elif is_qqguild(bot):
        puid = 'qqguild_' + puid
    return puid


# 检测适配器类型
def is_onebot_v11(bot: Bot) -> bool:
    if ob11:
        return isinstance(bot, ob11.Bot)
    return False


def is_onebot_v12(bot: Bot) -> bool:
    if ob12:
        return isinstance(bot, ob12.Bot)
    return False


def is_mirai2(bot: Bot) -> bool:
    if mirai2:
        return isinstance(bot, mirai2.Bot)
    return False


def is_kook(bot: Bot) -> bool:
    if kook:
        return isinstance(bot, kook.Bot)
    return False


def is_console(bot: Bot) -> bool:
    if console:
        return isinstance(bot, console.Bot)
    return False


def is_onebot(bot: Bot) -> bool:
    return is_onebot_v11(bot) or is_onebot_v12(bot)


def is_qqguild(bot: Bot) -> bool:
    if qqguild:
        return isinstance(bot, qqguild.Bot)
    return False


def is_qq(bot: Bot) -> bool:
    return is_onebot(bot) or is_mirai2(bot) or is_qqguild(bot)
