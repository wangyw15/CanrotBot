import base64

from nonebot.adapters import Bot, Event, MessageSegment
from nonebot.permission import Permission
import httpx

from .config import get_config

# different bots
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
    """Get group id from different adapters"""
    if ob11 and isinstance(event, ob11.GroupMessageEvent) or ob12 and isinstance(event, ob12.GroupMessageEvent):
        return str(event.group_id)
    elif mirai2 and isinstance(event, mirai2.GroupMessage):
        return str(event.sender.group.id)
    elif kook and isinstance(event, kook.event.ChannelMessageEvent):
        return str(event.group_id)
    return None


def get_user_id(event: Event) -> str | None:
    """Get user id from different adapters"""
    if ob11 and isinstance(event, ob11.MessageEvent) or ob12 and isinstance(event, ob12.MessageEvent):
        return str(event.user_id)
    elif mirai2 and (isinstance(event, mirai2.event.GroupMessage) or isinstance(event, mirai2.event.FriendMessage)):
        return str(event.get_user_id())
    elif kook and isinstance(event, kook.event.MessageEvent):
        return str(event.author_id)
    return None


async def get_user_name(event: Event, bot: Bot, default: str = None) -> str | None:
    """Get username from different adapters"""
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
    """Get bot name from different adapters"""
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
    """Generate group forward message for OneBot"""
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


async def fetch_bytes_data(url: str) -> bytes | None:
    """Fetch bytes from url"""
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        return resp.content
    return None


async def fetch_json_data(url: str) -> dict | None:
    """Fetch json from url"""
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None


async def get_image_message_from_url(bot: Bot, img_url: str) -> MessageSegment | None:
    """Get image MessageSegment by url for different adapters"""
    if ob11 and isinstance(bot, ob11.Bot):
        return ob11.MessageSegment.image(file=img_url)
    elif ob12 and isinstance(bot, ob12.Bot):
        resp = await bot.upload_file(type='url', url=img_url)
        return ob12.MessageSegment.image(file_id=resp.file_id)
    elif kook and isinstance(bot, kook.Bot):
        img_data = await fetch_bytes_data(img_url)
        if img_data:
            url = await bot.upload_file(img_data)
            return kook.MessageSegment.image(url)
    elif mirai2 and isinstance(bot, mirai2.Bot):
        return mirai2.MessageSegment.image(url=img_url)
    elif console and isinstance(bot, console.Bot):
        return console.MessageSegment.text(img_url)
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


async def send_image_from_url(img_url: str, bot: Bot, event: Event) -> None:
    if is_onebot_v11(bot):
        await bot.send(event, ob11.MessageSegment.image(file=img_url))
    elif is_onebot_v12(bot):
        await bot.send(event, ob12.MessageSegment.image(file_id=img_url))
    elif is_kook(bot):
        img_data = await fetch_bytes_data(img_url)
        if img_data:
            url = await bot.upload_file(img_data)
            await bot.send(event, kook.MessageSegment.image(url))
    else:
        await bot.send(event, f'图片链接: {img_url}')


async def send_image(img: bytes, bot: Bot, event: Event) -> bool:
    if is_onebot_v11(bot):
        await bot.send(event, ob11.MessageSegment.image(file=img))
        return True
    elif is_onebot_v12(bot):
        b64img = base64.b64encode(img).decode()
        await bot.send(event, ob12.Message(f'[CQ:image,file=base64://{b64img}]'))
        return True
    elif is_kook(bot):
        url = await bot.upload_file(img)
        await bot.send(event, kook.MessageSegment.image(url))
        return True
    return False


def get_puid(bot: Bot, event: Event) -> str:
    puid = get_user_id(event)
    if is_onebot_v11(bot) or is_onebot_v12(bot) or is_mirai2(bot):
        puid = 'qq_' + str(puid)
    elif is_kook(bot):
        puid = 'kook_' + str(puid)
    elif is_console(bot):
        puid = 'console_console'
    return puid


# detect bot type
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
