import asyncio
from io import BytesIO
from pathlib import Path

import nonebot.adapters.onebot.v12 as onebot_v12
from httpx import AsyncClient
from nonebot.matcher import current_bot

from . import AdapterInterface

_client = AsyncClient()


class OneBotV12(AdapterInterface):
    from . import message

    def generate_message(self, msg: message.Message) -> onebot_v12.Message:
        from . import message
        ret = onebot_v12.Message()
        for seg in msg:
            if seg.type == message.MessageSegmentTypes.TEXT:
                ret.append(onebot_v12.MessageSegment.text(seg.data['text']))
            elif seg.type == message.MessageSegmentTypes.IMAGE:
                img_data: bytes | None = None
                if isinstance(seg.data['file'], bytes):
                    img_data = seg.data['file']
                elif isinstance(seg.data['file'], BytesIO):
                    img_data = seg.data['file'].read()
                elif isinstance(seg.data['file'], str):
                    resp = asyncio.run(_client.get(seg.data['file']))
                    if resp.is_success and resp.status_code == 200:
                        img_data = resp.content
                elif isinstance(seg.data["file"], Path):
                    img_data = seg.data['file'].read_bytes()
                if img_data:
                    resp = await current_bot.get().upload_file(type='data', data=img_data)
                    if resp:
                        ret.append(onebot_v12.MessageSegment.image(resp['file_id']))
            elif seg.type == message.MessageSegmentTypes.AT:
                ret.append(onebot_v12.MessageSegment.mention(user_id=seg.data['user_id']))
        return ret

    def parse_message(self, msg: onebot_v12.Message) -> message.Message:
        from . import message
        ret = message.Message()
        for seg in msg:
            if seg.type == 'image':
                ret.append(message.MessageSegment.image(seg.data['file_id']))
            elif seg.type == 'mention':
                ret.append(message.MessageSegment.at(seg.data['user_id']))
            else:
                ret.append(str(seg))
        return ret


__all__ = ['OneBotV12']
