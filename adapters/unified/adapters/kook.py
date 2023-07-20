from io import BytesIO
from pathlib import Path

import nonebot.adapters.kaiheila as kook
from httpx import AsyncClient
from nonebot.adapters.kaiheila import Bot, Event
from nonebot.matcher import current_matcher, current_bot, current_event

from . import AdapterInterface

_client = AsyncClient()


class Kook(AdapterInterface):
    from . import message

    @staticmethod
    async def _kook_send_image(img: str | Path | bytes | BytesIO, bot: Bot, event: Event) -> bool:
        """
        KOOK

        :param img: 图片的`bytes`或者本地路径
        :param bot: 机器人实例
        :param event: 事件实例
        """
        url = ''
        if isinstance(img, str):
            img_data = None
            resp = await _client.get(img)
            if resp.is_success and resp.status_code == 200:
                url = await bot.upload_file(resp.content)
        elif isinstance(img, Path):
            with img.open('rb') as f:
                url = await bot.upload_file(f.read())
        elif isinstance(img, bytes):
            url = await bot.upload_file(img)
        elif isinstance(img, BytesIO):
            url = await bot.upload_file(img.read())
        if url:
            await bot.send(event, kook.MessageSegment.image(url))
            return True
        return False

    def generate_message(self, msg: message.Message) -> kook.Message:
        raise NotImplementedError('Kook消息需要特殊处理')

    def parse_message(self, msg: kook.Message) -> message.Message:
        from . import message
        ret = message.Message()
        for seg in msg:
            if seg.type == 'image':
                ret.append(message.MessageSegment.image(seg.data['file_key']))
            elif seg.type == 'text' or seg.type == 'kmarkdown':
                ret.append(seg.plain_text)
            else:
                ret.append(str(seg))
        return ret

    async def send(self, msg: message.Message) -> None:
        from . import message
        # KOOK 不支持图文混排，所以直接发送了
        tmp = ''
        for seg in msg:
            if seg.type == message.MessageSegmentTypes.IMAGE:
                if tmp.strip():
                    await current_matcher.get().send(tmp)
                    tmp = ''
                await self._kook_send_image(seg.data['file'], current_bot.get(), current_event.get())
            elif seg.type == message.MessageSegmentTypes.TEXT:
                tmp += seg.data['text']
        if tmp.strip():
            await current_matcher.get().send(tmp)


__all__ = ['Kook']
