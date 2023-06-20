import httpx
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='能不能好好说话',
    description='根据简写找原话',
    usage='/<nbnhhsh|能不能好好说话> <缩写>',
    config=None
)

_client = httpx.AsyncClient()


async def fetch_nbnhhsh(text: str) -> list[str] | None:
    url = 'https://lab.magiconch.com/api/nbnhhsh/guess'
    resp: list[dict] = (await _client.post(url, json={'text': text})).json()
    if resp:
        return resp[0]['trans']
    return None

nbnhhsh = on_command('nbnhhsh', aliases={'能不能好好说话'}, block=True)
@nbnhhsh.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        trans = await fetch_nbnhhsh(msg)
        if trans:
            await nbnhhsh.finish(f'{msg}: \n' + '\n'.join(trans))
        await nbnhhsh.finish('没有找到翻译')
    await nbnhhsh.finish('用法: /nbnhhsh <缩写>')
