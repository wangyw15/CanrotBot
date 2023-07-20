import nonebot.adapters.onebot.v11 as onebot_v11

from . import AdapterInterface


class OneBotV11(AdapterInterface):
    from . import message

    @classmethod
    async def generate_message(cls, msg: message.Message) -> onebot_v11.Message:
        from . import message
        ret = onebot_v11.Message()
        for seg in msg:
            if seg.type == message.MessageSegmentTypes.TEXT:
                ret.append(onebot_v11.MessageSegment.text(seg.data['text']))
            elif seg.type == message.MessageSegmentTypes.IMAGE:
                ret.append(onebot_v11.MessageSegment.image(seg.data['file']))
            elif seg.type == message.MessageSegmentTypes.AT:
                ret.append(onebot_v11.MessageSegment.at(seg.data['user_id']))
        return ret

    @classmethod
    async def parse_message(cls, msg: onebot_v11.Message) -> message.Message:
        from . import message
        ret = message.Message()
        for seg in msg:
            if seg.type == 'image':
                ret.append(message.MessageSegment.image(seg.data['url']))
            elif seg.type == 'at':
                ret.append(message.MessageSegment.at(seg.data['qq']))
            else:
                ret.append(str(seg))
        return ret


__all__ = ['OneBotV11']
