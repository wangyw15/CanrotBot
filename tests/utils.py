from datetime import datetime

from nonebot.adapters.console import Message, MessageEvent
from nonechat.info import User


def make_event(
        message: str = "",
        self_id: str = "test",
        user_id: str = "123456789"
) -> MessageEvent:
    return MessageEvent(
        time=datetime.now(),
        self_id=self_id,
        message=Message(message),
        user=User(id=user_id, nickname=user_id)
    )
