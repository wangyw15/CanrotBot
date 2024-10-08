from enum import Enum


class Platform(Enum):
    Console = "console"
    QQ = "qq"
    OneBotV11 = "onebot_v11"
    OneBotV12 = "onebot_v12"
    # Mirai2 = "mirai2"
    Kook = "kook"


class ChatType(Enum):
    Private = "private"
    Group = "group"
    Channel = "channel"


class PluginListMode(Enum):
    Blacklist = "blacklist"
    Whitelist = "whitelist"
