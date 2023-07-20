from nonebot.permission import Permission
from . import adapters


GROUP = Permission()
'''群聊消息事件'''
if adapters.onebot_v11_module:
    GROUP |= adapters.onebot_v11_module.GROUP
if adapters.onebot_v12_module:
    GROUP |= adapters.onebot_v12_module.GROUP
if adapters.mirai2_module:
    GROUP |= adapters.mirai2_module.GROUP_MEMBER | adapters.mirai2_module.GROUP_ADMINS
if adapters.kook_module:
    pass


GROUP_ADMIN = Permission()
'''群聊管理员事件'''
if adapters.onebot_v11_module:
    GROUP_ADMIN |= adapters.onebot_v11_module.GROUP_ADMIN
if adapters.mirai2_module:
    GROUP_ADMIN |= adapters.mirai2_module.GROUP_ADMINS


GROUP_OWNER = Permission()
'''Group owner permission for only mirai2 and onebot v11'''
if adapters.onebot_v11_module:
    GROUP_OWNER |= adapters.onebot_v11_module.GROUP_OWNER
if adapters.mirai2_module:
    GROUP_OWNER |= adapters.mirai2_module.GROUP_OWNER
