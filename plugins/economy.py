from nonebot import on_command
from nonebot.adapters import Bot, Event, Message
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata

from ..libraries import user, economy, universal_adapters

__plugin_meta__ = PluginMetadata(
    name='经济服务',
    description='经济服务，包括查询、转账等',
    usage='输入 /<economy|e|钱包|银行|经济> 查看帮助',
    config=None
)

_user = on_command('economy', aliases={'e', '钱包', '银行', '经济'}, block=True)
@_user.handle()
async def _(state: T_State, bot: Bot, event: Event, args: Message = CommandArg()):
    puid = universal_adapters.get_puid(bot, event)
    if msg := args.extract_plain_text():
        splitted_args = [x.strip() for x in msg.split()]
        if msg == 'info' or msg == '信息':
            if not user.puid_user_exists(puid):
                await _user.finish(f'puid: {puid}\n你还没有注册')
            else:
                uid = user.get_uid(puid)
                await _user.finish(f'puid: {puid}\nuid: {uid}\n当前余额: {economy.get_balance(uid)}')
        elif splitted_args[0] == 'transfer' or splitted_args[0] == '转账':
            another = splitted_args[1]
            amount = float(splitted_args[2])
            another_uid = ''
            if '_' in another:
                another_uid = user.get_uid(puid)
            else:
                another_uid = another
            if not user.puid_user_exists(another_uid):
                await _user.finish('不存在此用户')
            uid = user.get_uid(puid)
            economy.transfer(uid, another_uid, amount)
    else:
        await _user.finish('经济服务帮助:\n用法: /<economy|e|钱包|银行|经济> [操作]\n操作:\ninfo|信息: 查看账户信息\ntransfer|转账 <puid|uid> <金额>: 向另一个用户转账')