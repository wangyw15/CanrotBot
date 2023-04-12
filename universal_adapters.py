from nonebot.adapters import Bot, Event, Message, MessageSegment
from nonebot.permission import Permission
import requests

# different bots
try:
    import nonebot.adapters.onebot.v11 as ob11
except:
    ob11 = None
try:
    import nonebot.adapters.onebot.v12 as ob12
except:
    ob12 = None
try:
    import nonebot.adapters.kaiheila as kook
except:
    kook = None
try:
    import nonebot.adapters.mirai2 as mirai2
except:
    mirai2 = None
try:
    import nonebot.adapters.console as console
except:
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
    GROUP_OWNER |= mirai2.GROUP_OWNER

def get_group_id(event: Event) -> str | None:
    '''Get group id from different adapters'''
    if ob11 and isinstance(event, ob11.GroupMessageEvent) or ob12 and isinstance(event, ob12.GroupMessageEvent):
        return str(event.group_id)
    elif mirai2 and isinstance(event, mirai2.GroupMessage):
        return str(event.sender.group.id)
    elif kook and isinstance(event, kook.event.ChannelMessageEvent):
        return str(event.group_id)
    return None

def get_user_id(event: Event) -> str | None:
    '''Get user id from different adapters'''
    if ob11 and isinstance(event, ob11.MessageEvent) or ob12 and isinstance(event, ob12.MessageEvent):
        return str(event.user_id)
    elif mirai2 and (isinstance(event, mirai2.event.GroupMessage) or isinstance(event, mirai2.event.FriendMessage)):
        return str(event.get_user_id())
    elif kook and isinstance(event, kook.event.MessageEvent):
        return str(event.author_id)
    return None

async def get_user_name(event: Event, bot: Bot, default: str = None) -> str | None:
    '''Get user name from different adapters'''
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
        if isinstance(event, kook.Event):
            return event.extra.author.nikname
    return default

async def get_bot_name(event: Event, bot: Bot, default: str = None) -> str | None:
    '''Get bot name from different adapters'''
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
        # not implemented
        pass
    # kook
    elif kook and isinstance(bot, kook.Bot):
        if isinstance(event, kook.Event):
            return bot.self_name
    return default

def fetch_data(url: str) -> bytes | None:
    '''Fetch bytes from url'''
    resp = requests.get(url)
    if resp.ok and resp.status_code == 200:
        return resp.content
    return None

async def get_image_message(bot: Bot, img_url: str) -> MessageSegment:
    '''Get image MessageSegement for different adapters'''
    if ob11 and isinstance(bot, ob11.Bot):
        return ob11.MessageSegment.image(file = img_url)
    elif ob12 and isinstance(bot, ob12.Bot):
        return ob12.MessageSegment.image(file = img_url)
    elif kook and isinstance(bot, kook.Bot):
        img_data = fetch_data(img_url)
        if img_data:
            url = await bot.upload_file(img_data)
            return kook.MessageSegment.image(url)
    elif mirai2 and isinstance(bot, mirai2.Bot):
        return mirai2.MessageSegment.image(url = img_url)
    else:
        return MessageSegment.text(img_url)

# detect bot type
def is_onebot_v11(bot: Bot) -> bool:
    return isinstance(bot, ob11.Bot)

def is_onebot_v12(bot: Bot) -> bool:
    return isinstance(bot, ob12.Bot)

def is_mirai2(bot: Bot) -> bool:
    return isinstance(bot, mirai2.Bot)

def is_kook(bot: Bot) -> bool:
    return isinstance(bot, kook.Bot)

def is_console(bot: Bot) -> bool:
    return isinstance(bot, console.Bot)
