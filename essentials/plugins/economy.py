from nonebot import on_command
from nonebot.adapters import Bot, Event, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from essentials.libraries import user, economy
from datetime import datetime

__plugin_meta__ = PluginMetadata(
    name='经济服务',
    description='经济服务，包括查询、转账等',
    usage='经济服务帮助:\n用法: /<economy|e|钱包|银行|经济> [操作]\n操作:\ninfo|信息: 查看账户信息\ntransfer|转账 <puid|uid> <金额>: 向另一个用户转账',
    config=None
)

_economy = on_command('economy', aliases={'e', '钱包', '银行', '经济', 'bank'}, block=True)
@_economy.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    # check if registered
    puid = user.get_puid(bot, event)
    if not user.puid_user_exists(puid):
        await _economy.finish(f'puid: {puid}\n你还没有注册')
    
    uid = user.get_uid(puid)
    if msg := args.extract_plain_text():
        splitted_args = [x.strip().lower() for x in msg.split()]
        if msg == 'info' or msg == '信息' or msg == 'balance' or msg == '余额':
            final = f'puid: {puid}\nuid: {uid}\n当前余额: {economy.get_balance(uid)} 胡萝卜片\n\n最近五条交易记录:'
            history = economy.get_history(uid)
            for i in history[:5]:
                final += f"\n时间: {datetime.fromisoformat(i['time']).strftime('%Y-%m-%d %H:%M:%S')}" \
                         f"\n变动: {i['amount']}" \
                         f"\n余额: {i['balance']}" \
                         f"\n备注: {i['description']}" \
                         f"\n--------------------"
            await _economy.finish(final)
        elif splitted_args[0] == 'transfer' or splitted_args[0] == '转账':
            another = splitted_args[1]
            amount = float(splitted_args[2])
            another_uid = ''
            if '_' in another:
                another_uid = user.get_uid(another)
            else:
                another_uid = another
            if not user.uid_user_exists(another_uid):
                await _economy.finish('不存在此用户')
            if economy.transfer(uid, another_uid, amount):
                await _economy.finish(f'向 uid {another_uid} 转账 {amount} 个胡萝卜片成功')
            else:
                await _economy.finish(f'向 uid {another_uid} 转账 {amount} 个胡萝卜片失败')
    else:
        await _economy.finish(__plugin_meta__.usage)
