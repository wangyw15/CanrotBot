import base64
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Type, Iterable

from nonebot.adapters import Bot, Event
from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment
from nonebot.typing import overrides

from . import adapters
from .detector import Detector
from essentials.libraries import util


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

    async def send(self, bot: Bot, event: Event) -> None:
        await Message([self]).send(bot, event)

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

    @staticmethod
    async def _kook_send_image(img: str | Path | bytes | BytesIO, bot: Bot, event: Event) -> bool:
        """
        KOOK

        :param img: 图片的`bytes`或者本地路径
        :param bot: 机器人实例
        :param event: 事件实例
        """
        if Detector.is_kook(bot):
            url = ''
            if isinstance(img, str):
                img_data = await util.fetch_bytes_data(img)
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
                await bot.send(event, adapters.kook.MessageSegment.image(url))
                return True
        return False

    async def send(self, bot: Bot, event: Event) -> None:
        final_msg: Message = Message()
        # 构建消息
        if Detector.is_onebot_v11(bot):
            for seg in self:
                if seg.type == MessageSegmentTypes.TEXT:
                    final_msg.append(adapters.onebot_v11.MessageSegment.text(seg.data['text']))
                elif seg.type == MessageSegmentTypes.IMAGE:
                    final_msg.append(adapters.onebot_v11.MessageSegment.image(seg.data['file']))
                elif seg.type == MessageSegmentTypes.AT:
                    final_msg.append(adapters.onebot_v11.MessageSegment.at(seg.data['user_id']))
        elif Detector.is_onebot_v12(bot):
            for seg in self:
                if seg.type == MessageSegmentTypes.TEXT:
                    final_msg.append(adapters.onebot_v12.MessageSegment.text(seg.data['text']))
                elif seg.type == MessageSegmentTypes.IMAGE:
                    img_data: bytes | None = None
                    if isinstance(seg.data['file'], bytes):
                        img_data = seg.data['file']
                    elif isinstance(seg.data['file'], BytesIO):
                        img_data = seg.data['file'].read()
                    elif isinstance(seg.data['file'], str):
                        img_data = await util.fetch_bytes_data(seg.data['file'])
                    elif isinstance(seg.data["file"], Path):
                        img_data = seg.data['file'].read_bytes()
                    if img_data:
                        resp = await bot.upload_file(type='data', data=img_data)
                        if resp:
                            final_msg.append(adapters.onebot_v12.MessageSegment.image(resp['file_id']))
                elif seg.type == MessageSegmentTypes.AT:
                    final_msg.append(adapters.onebot_v12.MessageSegment.mention(user_id=seg.data['user_id']))
        elif Detector.is_mirai2(bot):
            for seg in self:
                if seg.type == MessageSegmentTypes.TEXT:
                    final_msg.append(adapters.mirai2.MessageSegment.plain(seg.data['text']))
                elif seg.type == MessageSegmentTypes.IMAGE:
                    if isinstance(seg.data['file'], str):
                        final_msg.append(adapters.mirai2.MessageSegment.image(url=seg.data['file']))
                    elif isinstance(seg.data['file'], Path):
                        final_msg.append(adapters.mirai2.MessageSegment.image(path=str(seg.data['file'])))
                    elif isinstance(seg.data['file'], bytes):
                        b64img = base64.b64encode(seg.data['file']).decode()
                        final_msg.append(adapters.mirai2.MessageSegment.image(base64=b64img))
                    elif isinstance(seg.data['file'], BytesIO):
                        b64img = base64.b64encode(seg.data['file'].read()).decode()
                        final_msg.append(adapters.mirai2.MessageSegment.image(base64=b64img))
                elif seg.type == MessageSegmentTypes.AT:
                    final_msg.append(adapters.mirai2.MessageSegment.at(seg.data['user_id']))
        elif Detector.is_qqguild(bot):
            for seg in self:
                if seg.type == MessageSegmentTypes.TEXT:
                    final_msg.append(adapters.qqguild.MessageSegment.text(seg.data['text']))
                elif seg.type == MessageSegmentTypes.IMAGE:
                    if isinstance(seg.data['file'], str):
                        # 为了能发送所有图片，这里直接下载了
                        file_data = await util.fetch_bytes_data(seg.data['file'])
                        if file_data:
                            final_msg.append(adapters.qqguild.MessageSegment.file_image(file_data))
                        else:
                            final_msg.append(f'\n{str(seg)}\n')
                    else:
                        final_msg.append(adapters.qqguild.MessageSegment.file_image(seg.data['file']))
                elif seg.type == MessageSegmentTypes.AT:
                    final_msg.append(adapters.qqguild.MessageSegment.mention_user(seg.data['user_id']))
        elif Detector.is_kook(bot):
            # KOOK 不支持图文混排，所以直接发送了
            tmp = ''
            for seg in self:
                if seg.type == MessageSegmentTypes.IMAGE:
                    if tmp.strip():
                        await bot.send(event, tmp)
                        tmp = ''
                    await self._kook_send_image(seg.data['file'], bot, event)
                elif seg.type == MessageSegmentTypes.TEXT:
                    tmp += seg.data['text']
            if tmp.strip():
                await bot.send(event, tmp)
            return
        else:
            final_msg: str = ''  # 在 console 有莫名其妙的问题，所以改为 str
            for seg in self:
                if seg.type == MessageSegmentTypes.TEXT:
                    final_msg += seg.data['text']
                elif seg.type == MessageSegmentTypes.IMAGE:
                    final_msg += f'\n{str(seg)}\n'
                elif seg.type == MessageSegmentTypes.AT:
                    final_msg += f'@{seg.data["user_id"]}'
            final_msg: str = final_msg.strip()

        await bot.send(event, final_msg)

    @staticmethod
    async def send_file(content: bytes, name: str, bot: Bot, event: Event):
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
