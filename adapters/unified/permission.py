from nonebot.permission import Permission
from . import adapters


GROUP = Permission()
'''群聊消息事件'''
if adapters.onebot_v11:
    GROUP |= adapters.onebot_v11.GROUP
if adapters.onebot_v12:
    GROUP |= adapters.onebot_v12.GROUP
if adapters.mirai2:
    GROUP |= adapters.mirai2.GROUP_MEMBER | adapters.mirai2.GROUP_ADMINS
if adapters.kook:
    pass


GROUP_ADMIN = Permission()
'''群聊管理员事件'''
if adapters.onebot_v11:
    GROUP_ADMIN |= adapters.onebot_v11.GROUP_ADMIN
if adapters.mirai2:
    GROUP_ADMIN |= adapters.mirai2.GROUP_ADMINS


GROUP_OWNER = Permission()
'''Group owner permission for only mirai2 and onebot v11'''
if adapters.onebot_v11:
    GROUP_OWNER |= adapters.onebot_v11.GROUP_OWNER
if adapters.mirai2:
    GROUP_OWNER |= adapters.mirai2.GROUP_OWNER
