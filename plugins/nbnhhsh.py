from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
import requests

from ..data import add_help_message

add_help_message('nbnhhsh', '能不能好好说话，用法: /nbnhhsh <缩写>')

def fetch_nbnhhsh(text: str) -> list[str]:
    url = 'https://lab.magiconch.com/api/nbnhhsh/guess'
    resp: list[dict] = requests.post(url, json={'text': text}).json()
    if resp:
        return resp[0]['trans']
    return None

nbnhhsh = on_command('nbnhhsh', aliases={'能不能好好说话'}, block=True)
@nbnhhsh.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        trans = fetch_nbnhhsh(msg)
        if trans:
            await nbnhhsh.finish(f'{msg}: \n' + '\n'.join(trans))
        await nbnhhsh.finish('没有找到翻译')
    await nbnhhsh.finish('用法: /nbnhhsh <缩写>')
