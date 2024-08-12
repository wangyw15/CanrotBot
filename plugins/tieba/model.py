from enum import Enum


class ForumSigninResultType(Enum):
    """
    贴吧签到结果类型
    """

    SUCCESS = 0
    ALREADY_SIGNED = 1
    ERROR = 2
