import base64
from io import BytesIO
from pathlib import Path

import nonebot.adapters.mirai2 as mirai2

from . import AdapterInterface


class Mirai2(AdapterInterface):
    from . import message

    @classmethod
    async def generate_message(cls, msg: message.Message) -> mirai2.MessageChain:
        from . import message
        ret = mirai2.MessageChain()
        for seg in msg:
            if seg.type == message.MessageSegmentTypes.TEXT:
                ret.append(mirai2.MessageSegment.plain(seg.data['text']))
            elif seg.type == message.MessageSegmentTypes.IMAGE:
                if isinstance(seg.data['file'], str):
                    ret.append(mirai2.MessageSegment.image(url=seg.data['file']))
                elif isinstance(seg.data['file'], Path):
                    ret.append(mirai2.MessageSegment.image(path=str(seg.data['file'])))
                elif isinstance(seg.data['file'], bytes):
                    b64img = base64.b64encode(seg.data['file']).decode()
                    ret.append(mirai2.MessageSegment.image(base64=b64img))
                elif isinstance(seg.data['file'], BytesIO):
                    b64img = base64.b64encode(seg.data['file'].read()).decode()
                    ret.append(mirai2.MessageSegment.image(base64=b64img))
            elif seg.type == message.MessageSegmentTypes.AT:
                ret.append(mirai2.MessageSegment.at(seg.data['user_id']))
        return ret

    @classmethod
    async def parse_message(cls, msg: mirai2.MessageChain) -> message.Message:
        from . import message
        ret = message.Message()
        for seg in msg:
            if seg.type == mirai2.MessageType.PLAIN:
                ret.append(message.MessageSegment.text(seg.data['text']))
            elif seg.type == mirai2.MessageType.IMAGE:
                ret.append(message.MessageSegment.image(seg.data['url']))
            elif seg.type == mirai2.MessageType.AT:
                ret.append(message.MessageSegment.at(seg.data['target']))
            else:
                ret.append(str(seg))
        return ret


__all__ = ['Mirai2']
