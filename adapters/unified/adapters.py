# 不同适配器
try:
    import nonebot.adapters.onebot.v11 as onebot_v11
except ModuleNotFoundError:
    onebot_v11 = None
try:
    import nonebot.adapters.onebot.v12 as onebot_v12
except ModuleNotFoundError:
    onebot_v12 = None
try:
    import nonebot.adapters.mirai2 as mirai2
except ModuleNotFoundError:
    mirai2 = None
try:
    import nonebot.adapters.qqguild as qqguild
except ModuleNotFoundError:
    qqguild = None
try:
    import nonebot.adapters.kaiheila as kook
except ModuleNotFoundError:
    kook = None
try:
    import nonebot.adapters.console as console
except ModuleNotFoundError:
    console = None


__all__ = ['onebot_v11', 'onebot_v12', 'mirai2', 'qqguild', 'kook', 'console']
