import importlib
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Type, Iterable

from nonebot.adapters import Bot, Event
from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment
from nonebot.matcher import current_bot
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

    async def send(self, bot: Bot) -> None:
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
        for i in dir(adapters.SupportedAdapters):
            if i.startswith('_'):
                continue
            if current_bot.get().__class__ == getattr(adapters.SupportedAdapters, i).Bot:
                module = importlib.import_module(f'.adapters.{adapters.SupportedAdaptersName[i]}', __package__)
                adapter: adapters.AdapterInterface = getattr(module, i)
                await adapter.send(self)
                break

    @staticmethod
    async def send_file(content: bytes, name: str, bot: Bot, event: Event):
        from . import adapters
        if Detector.is_onebot(bot):
            with NamedTemporaryFile() as f:
                f.write(content)
                f.flush()
                if isinstance(event, adapters.onebot_v11.PrivateMessageEvent) \
                        or isinstance(event, adapters.onebot_v12.PrivateMessageEvent):
                    await bot.call_api('upload_private_file', user_id=event.get_user_id(), file=f.name, name=name)
                elif isinstance(event, adapters.onebot_v11.GroupMessageEvent) \
                        or isinstance(event, adapters.onebot_v12.GroupMessageEvent):
                    await bot.call_api('upload_group_file', group_id=event.group_id, file=f.name, name=name)
        elif isinstance(bot, adapters.kook.Bot):
            url = await bot.upload_file(content)
            await bot.send(event, adapters.kook.MessageSegment.file(url, name))
        else:
            await bot.send(event, f'[此处暂不支持发送文件，文件名: {name}]')


__all__ = ['MessageSegmentTypes', 'MessageSegment', 'Message']
