import nonebot.adapters.onebot.v11 as onebot_v11

from . import AdapterInterface


class OneBotV11(AdapterInterface):
    from . import message

    def generate_message(self, msg: message.Message) -> onebot_v11.Message:
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

    def parse_message(self, msg: onebot_v11.Message) -> message.Message:
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
