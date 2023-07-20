import asyncio

import nonebot.adapters.qqguild as qq_guild
from httpx import AsyncClient

from . import AdapterInterface

_client = AsyncClient()


class QQGuild(AdapterInterface):
    from . import message

    def generate_message(self, msg: message.Message) -> qq_guild.Message:
        from . import message
        ret = qq_guild.Message()
        for seg in msg:
            if seg.type == message.MessageSegmentTypes.TEXT:
                ret.append(qq_guild.MessageSegment.text(seg.data['text']))
            elif seg.type == message.MessageSegmentTypes.IMAGE:
                if isinstance(seg.data['file'], str):
                    # 为了能发送所有图片，这里直接下载了
                    resp = asyncio.run(_client.get(seg.data['file']))
                    if resp.is_success and resp.status_code == 200:
                        ret.append(qq_guild.MessageSegment.file_image(resp.content))
                    else:
                        ret.append(f'\n{str(seg)}\n')
                else:
                    ret.append(qq_guild.MessageSegment.file_image(seg.data['file']))
            elif seg.type == message.MessageSegmentTypes.AT:
                ret.append(qq_guild.MessageSegment.mention_user(seg.data['user_id']))
        return ret

    def parse_message(self, msg: qq_guild.Message) -> message.Message:
        from . import message
        ret = message.Message()
        for seg in msg:
            if seg.type == 'attachment':
                ret.append(message.MessageSegment.image(seg.data['url']))
            elif seg.type == 'mention_user':
                ret.append(message.MessageSegment.at(seg.data['user_id']))
            else:
                ret.append(str(seg))
        return ret


__all__ = ['QQGuild']

