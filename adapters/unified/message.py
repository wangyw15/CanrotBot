import base64
import json
from enum import Enum
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Type, Tuple, Union, Mapping, Iterable, Dict, cast, Optional

from deprecated import deprecated
from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment
from nonebot.internal.adapter.message import TMS, TM
from nonebot.typing import overrides
from nonebot.adapters import Bot, Event
from nonebot import logger

from .adapters import Adapters
from .detector import Detector
from .util import fetch_bytes_data


class MessageSegmentTypes(Enum):
    TEXT = 'text'
    IMAGE = 'image'
    AT = 'at'


class MessageSegment(BaseMessageSegment['Message']):
    @classmethod
    @overrides(BaseMessageSegment)
    def get_message_class(cls) -> Type['Message']:
        return Message

    def __str__(self) -> str:
        if self.type == MessageSegmentTypes.TEXT.value:
            return str(self.data['text'])
        elif self.type == MessageSegmentTypes.IMAGE.value:
            if 'alt' in self.data:
                return f'[图片描述: {self.data["alt"]}]'
            else:
                return '[图片]'
        elif self.type == MessageSegmentTypes.AT.value:
            return f'@{self.data["user_name"]}'
        else:
            return f'[不支持的消息类型: {self.type}]'

    def is_text(self) -> bool:
        return self.type == MessageSegmentTypes.TEXT.value

    async def send(self, bot: Bot, event: Event) -> None:
        await Message([self]).send(bot, event)

    @staticmethod
    def text(text: str) -> 'MessageSegment':
        return MessageSegment(MessageSegmentTypes.TEXT.value, {'text': text})

    @staticmethod
    def image(file: str | bytes | BytesIO | Path, alt='') -> 'MessageSegment':
        if alt:
            return MessageSegment(MessageSegmentTypes.IMAGE.value, {'file': file, 'alt': alt})
        else:
            return MessageSegment(MessageSegmentTypes.IMAGE.value, {'file': file})

    @staticmethod
    def at(user_id: int) -> 'MessageSegment':
        return MessageSegment(MessageSegmentTypes.AT.value, {'user_id': user_id})


class Message(BaseMessage[MessageSegment]):
    @classmethod
    @overrides(BaseMessage)
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @staticmethod
    @overrides(BaseMessage)
    def _construct(msg: str) -> Iterable[MessageSegment]:
        yield MessageSegment.text(msg)

    @staticmethod
    async def _kook_send_image(img: str | Path | bytes | BytesIO, bot: Bot, event: Event) -> bool:
        """
        KOOK

        :param img: 图片的`bytes`或者本地路径
        :param bot: 机器人实例
        :param event: 事件实例
        """
        if Detector.is_kook(bot):
            if isinstance(img, str):
                img_data = await fetch_bytes_data(img)
                if img_data:
                    url = await bot.upload_file(img_data)
            elif isinstance(img, Path):
                with img.open('rb') as f:
                    url = await bot.upload_file(f.read())
            elif isinstance(img, bytes):
                url = await bot.upload_file(img)
            elif isinstance(img, BytesIO):
                url = await bot.upload_file(img.read())
            if url:
                await bot.send(event, Adapters.KOOK.value.MessageSegment.image(url))
                return True
        return False

    async def send(self, bot: Bot, event: Event) -> None:
        final_msg: Message = Message()
        # 构建消息
        if Detector.is_onebot_v11(bot):
            for seg in self:
                if seg.type == MessageSegmentTypes.TEXT.value:
                    final_msg.append(Adapters.ONEBOT_V11.value.MessageSegment.text(seg.data['text']))
                elif seg.type == MessageSegmentTypes.IMAGE.value:
                    final_msg.append(Adapters.ONEBOT_V11.value.MessageSegment.image(seg.data['file']))
                elif seg.type == MessageSegmentTypes.AT.value:
                    final_msg.append(Adapters.ONEBOT_V11.value.MessageSegment.at(seg.data['user_id']))
        elif Detector.is_onebot_v12(bot):
            for seg in self:
                if seg.type == MessageSegmentTypes.TEXT.value:
                    final_msg.append(Adapters.ONEBOT_V12.value.MessageSegment.text(seg.data['text']))
                elif seg.type == MessageSegmentTypes.IMAGE.value:
                    if isinstance(seg.data["file"], bytes):
                        b64img = base64.b64encode(seg.data["file"]).decode()
                        final_msg.append(Adapters.ONEBOT_V12.value.Message(f'[CQ:image,file=base64://{b64img}]'))
                    elif isinstance(seg.data["file"], BytesIO):
                        b64img = base64.b64encode(seg.data["file"].read()).decode()
                        final_msg.append(Adapters.ONEBOT_V12.value.Message(f'[CQ:image,file=base64://{b64img}]'))
                    elif isinstance(seg.data["file"], str) or isinstance(seg.data["file"], Path):
                        final_msg.append(Adapters.ONEBOT_V12.value.Message(f'[CQ:image,file={seg.data["file"]}]'))
                elif seg.type == MessageSegmentTypes.AT.value:
                    final_msg.append(Adapters.ONEBOT_V12.value.MessageSegment.at(seg.data['user_id']))
        elif Detector.is_mirai2(bot):
            for seg in self:
                if seg.type == MessageSegmentTypes.TEXT.value:
                    final_msg.append(Adapters.MIRAI2.value.MessageSegment.plain(seg.data['text']))
                elif seg.type == MessageSegmentTypes.IMAGE.value:
                    if isinstance(seg.data['file'], str):
                        final_msg.append(Adapters.MIRAI2.value.MessageSegment.image(url=seg.data['file']))
                    elif isinstance(seg.data['file'], Path):
                        final_msg.append(Adapters.MIRAI2.value.MessageSegment.image(path=str(seg.data['file'])))
                    elif isinstance(seg.data['file'], bytes):
                        b64img = base64.b64encode(seg.data['file']).decode()
                        final_msg.append(Adapters.MIRAI2.value.MessageSegment.image(base64=b64img))
                    elif isinstance(seg.data['file'], BytesIO):
                        b64img = base64.b64encode(seg.data['file'].read()).decode()
                        final_msg.append(Adapters.MIRAI2.value.MessageSegment.image(base64=b64img))
                elif seg.type == MessageSegmentTypes.AT.value:
                    final_msg.append(Adapters.MIRAI2.value.MessageSegment.at(seg.data['user_id']))
        elif Detector.is_qqguild(bot):
            for seg in self:
                if seg.type == MessageSegmentTypes.TEXT.value:
                    final_msg.append(Adapters.QQGUILD.value.MessageSegment.text(seg.data['text']))
                elif seg.type == MessageSegmentTypes.IMAGE.value:
                    if isinstance(seg.data['file'], str):
                        final_msg.append(Adapters.QQGUILD.value.MessageSegment.image(seg.data['file']))
                    else:
                        final_msg.append(Adapters.QQGUILD.value.MessageSegment.file_image(seg.data['file']))
                elif seg.type == MessageSegmentTypes.AT.value:
                    final_msg.append(Adapters.QQGUILD.value.MessageSegment.mention_user(seg.data['user_id']))
        elif Detector.is_kook(bot):
            # KOOK 不支持图文混排，所以直接发送了
            tmp = ''
            for seg in self:
                if seg.type == MessageSegmentTypes.IMAGE.value:
                    if tmp.strip():
                        await bot.send(event, tmp)
                        tmp = ''
                    await self._kook_send_image(seg.data['file'], bot, event)
                elif seg.type == MessageSegmentTypes.TEXT.value:
                    tmp += seg.data['text']
            if tmp.strip():
                await bot.send(event, tmp)
            return
        else:
            final_msg: str = ''  # 在 console 有莫名其妙的问题，所以改为 str
            for seg in self:
                if seg.type == MessageSegmentTypes.TEXT.value:
                    final_msg += seg.data['text']
                elif seg.type == MessageSegmentTypes.IMAGE.value:
                    if 'alt' in seg.data:
                        final_msg += f'\n[图片描述: {seg.data["alt"]}]\n'
                    else:
                        final_msg += '\n[图片]\n'
                elif seg.type == MessageSegmentTypes.AT.value:
                    final_msg += f'@{seg.data["user_id"]}'

        await bot.send(event, final_msg)


__all__ = ['MessageSegmentTypes', 'MessageSegment', 'Message']
