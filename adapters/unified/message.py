from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Type, Iterable

from nonebot.adapters import Bot, Event
from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment
from nonebot.typing import overrides

from .detector import Detector


class MessageSegmentTypes:
    TEXT = 'text'
    IMAGE = 'image'
    AT = 'at'


class MessageSegment(BaseMessageSegment['Message']):
    @classmethod
    @overrides(BaseMessageSegment)
    def get_message_class(cls) -> Type['Message']:
        return Message

    def __str__(self) -> str:
        if self.type == MessageSegmentTypes.TEXT:
            return str(self.data['text'])
        elif self.type == MessageSegmentTypes.IMAGE:
            if 'alt' in self.data:
                return f'[图片描述: {self.data["alt"]}]'
            else:
                return '[图片]'
        elif self.type == MessageSegmentTypes.AT:
            return f'@{self.data["user_name"]}'
        else:
            return f'[不支持的消息类型: {self.type}]'

    def is_text(self) -> bool:
        return self.type == MessageSegmentTypes.TEXT

    async def send(self) -> None:
        await Message([self]).send()

    @staticmethod
    def text(text: str) -> 'MessageSegment':
        return MessageSegment(MessageSegmentTypes.TEXT, {'text': text})

    @staticmethod
    def image(file: str | bytes | BytesIO | Path, alt='') -> 'MessageSegment':
        if alt:
            return MessageSegment(MessageSegmentTypes.IMAGE, {'file': file, 'alt': alt})
        else:
            return MessageSegment(MessageSegmentTypes.IMAGE, {'file': file})

    @staticmethod
    def at(user_id: int) -> 'MessageSegment':
        return MessageSegment(MessageSegmentTypes.AT, {'user_id': user_id})


class Message(BaseMessage[MessageSegment]):
    @classmethod
    @overrides(BaseMessage)
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @staticmethod
    @overrides(BaseMessage)
    def _construct(msg: str) -> Iterable[MessageSegment]:
        yield MessageSegment.text(msg)

    async def send(self) -> None:
        from . import adapters
        await adapters.get_adapter().send(self)


__all__ = ['MessageSegmentTypes', 'MessageSegment', 'Message']
