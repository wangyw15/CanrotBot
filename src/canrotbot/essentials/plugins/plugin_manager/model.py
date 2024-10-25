from enum import Enum

ACTION = "action"
SCOPE = "scope"
PLATFORM = "platform"
PLATFORM_ID = "platform_id"
PLUGIN_ID = "plugin_id"
ALL_PLUGINS = "_all"


class Scope(Enum):
    PRIVATE_CHAT = "private"
    GROUP_CHAT = "group"
    GLOBAL = "global"
