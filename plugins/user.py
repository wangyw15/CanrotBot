from nonebot import on_command
from nonebot.adapters import Bot, Event, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from ..libraries import user

__plugin_meta__ = PluginMetadata(
    name='用户服务',
    description='用户服务，包括绑定、注册等',
    usage='输入 /<user|u|用户|我> 查看帮助',
    config=None
)

_user = on_command('user', aliases={'u', '用户', '我'}, block=True)
@_user.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    puid = user.get_puid(bot, event)
    if msg := args.extract_plain_text():
        splitted_args = [x.strip() for x in msg.split()]
        if msg == 'register' or msg == 'reg' or msg == '注册':
            if user.puid_user_exists(puid):
                await _user.finish('你已经注册过了')
            else:
                uid = user.register(puid)
                await _user.finish(f'注册成功，你的 UID 是 {uid}')
        elif msg == 'info' or msg == '信息':
            if not user.puid_user_exists(puid):
                await _user.finish(f'puid: {puid}\n你还没有注册')
            else:
                uid = user.get_uid(puid)
                msg = f'puid: {puid}\nuid: {uid}\n已绑定的 puid:\n'
                linked_accounts = user.get_bind_by_uid(uid)
                for i in linked_accounts:
                    msg += i + '\n'
                await _user.finish(msg.strip())
        elif splitted_args[0] == 'bind' or splitted_args[0] == '绑定':
            another_puid = splitted_args[1]
            if user.puid_user_exists(another_puid):
                await _user.finish('该用户已经绑定或注册过了')
            uid = user.get_uid(puid)
            user.bind(another_puid, uid)
            await _user.finish('绑定成功')
        elif splitted_args[0] == 'unbind' or splitted_args[0] == '解绑' or splitted_args[0] == '解除绑定':
            another_puid = splitted_args[1]
            if not user.puid_user_exists(another_puid):
                await _user.finish('该用户还没有绑定或注册')
            user.unbind(another_puid)
            await _user.finish('解绑成功')
    else:
        await _user.finish('用户服务帮助:\n用法: /<user|u|用户|我> [操作]\n操作:\nregister|reg|注册: 注册一个新用户\ninfo|信息: 查看用户信息\nbind|绑定 <puid>: 绑定一个用户\nunbind|解绑|解除绑定 <puid>: 解除绑定一个用户')
