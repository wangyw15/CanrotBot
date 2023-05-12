from nonebot import on_command, get_driver
from nonebot.params import CommandArg, Arg
from nonebot.adapters import Bot, Event, Message
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from pydantic import BaseModel, validator
import httpx

from ..universal_adapters import is_onebot_v11, is_onebot_v12, is_mirai2, is_kook, is_console

from nonebot import logger

__plugin_meta__ = PluginMetadata(
    name='识图',
    description='通过 SauceNAO 识图',
    usage='先发送/<识图>，再发图片或者图片链接',
    config=None
)

class SearchImageConfig(BaseModel):
    canrot_proxy: str = ''
    saucenao_api_key: str = ''
    sauce_nao_numres: int = 5

    @validator('saucenao_api_key')
    def saucenao_api_key_validator(cls, v):
        if (not v) or (not isinstance(v, str)):
            raise ValueError('saucenao_api_key must be a str')
        return v
    
    @validator('sauce_nao_numres')
    def sauce_nao_numres_validator(cls, v):
        if (not v) or (not isinstance(v, int)):
            raise ValueError('sauce_nao_numres must be a int')
        return v

_config = SearchImageConfig.parse_obj(get_driver().config)
if _config.canrot_proxy:
    _client = httpx.AsyncClient(proxies=_config.canrot_proxy)
else:
    _client = httpx.AsyncClient()

async def search_image_from_saucenao(img_url: str) -> dict | None:
    api_url = 'https://saucenao.com/search.php?db=999&output_type=2&testmode=1&numres={numres}&api_key={api_key}&url={url}'
    resp = await _client.get(api_url.format(api_key=_config.saucenao_api_key, url=img_url, numres=_config.sauce_nao_numres))
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None

_search_image = on_command('识图', aliases={'搜图'}, block=True)
@_search_image.handle()
async def _(state: T_State, bot: Bot, args: Message = CommandArg()):
    api = 'saucenao'
    if msg := args.extract_plain_text():
        if msg == 'saucenao':
            api = 'saucenao'
        elif msg == 'tracemoe':
            api = 'tracemoe'
        else:
            await _search_image.finish('无效的搜图网站选项')
    state['SEARCH_IMAGE_API'] = api
    
    if is_console(bot):
        await _search_image.send('请发送图片链接')
    elif is_onebot_v11(bot):
        await _search_image.send('请发送图片或图片链接')
    else:
        await _search_image.finish('此平台暂未适配')

@_search_image.got('image')
async def _(state: T_State, bot: Bot, event: Event, image: Message = Arg()):
    # get img url
    img_url: str = ''
    if is_console(bot):
        img_url = image.extract_plain_text()
    elif is_onebot_v11(bot) or is_onebot_v12(bot):
        if image[0].type == 'image':
            img_url = image[0].data['url']
        elif image[0].type == 'text':
            img_url = image[0].data['text']
        else:
            await _search_image.reject('请重新发送图片或图片链接')
    else:
        _search_image.finish('此平台暂未适配')
    img_url = img_url.strip()
    
    # search
    if img_url:
        api: str = state['SEARCH_IMAGE_API']
        if api == 'saucenao':
            search_resp = await search_image_from_saucenao(img_url)
            if search_resp:
                # limits
                if 'header' in search_resp:
                    header: dict = search_resp['header']
                    if 'long_remaining' in header:
                        if header['long_remaining'] < 1:
                            await _search_image.finish('今日搜索次数已用完')
                        await _search_image.send(f'今日剩余搜索次数（每日重置）：{header["long_remaining"]}')
                    if 'short_remaining' in header:
                        if header['short_remaining'] < 1:
                            await _search_image.finish('30秒内搜索次数已用完')
                        await _search_image.send(f'当前剩余搜索次数（半分钟重置）：{header["short_remaining"]}')

                msg = '搜图结果：\n'
                results: list[dict] = search_resp['results']
                for result in results:
                    header: dict = result['header']
                    data: dict = result['data']

                    # title
                    if 'title' in data:
                        msg += data['title'] + '\n'
                    elif 'eng_name' in data:
                        msg += data['eng_name'] + '\n'
                    elif 'jp_name' in data:
                        msg += data['jp_name'] + '\n'
                    
                    # urls
                    if 'ext_urls' in data:
                        msg += '链接：\n'
                        for url in data['ext_urls']:
                            msg += url + '\n'

                    # pixiv
                    if 'pixiv_id' in data:
                        msg += f'Pixiv图片链接：https://www.pixiv.net/artworks/{data["pixiv_id"]}\n'
                    if 'member_name' in data:
                        msg += f'Pixiv作者名：{data["member_name"]}\n'
                    if 'member_id' in data:
                        msg += f'Pixiv作者链接：https://www.pixiv.net/users/{data["member_id"]}\n'

                    msg += '相似度：' + header['similarity'] + '\n'
                    msg += '--------------------\n'
                await _search_image.finish(msg)
            else:
                await _search_image.finish('搜索失败')
    else:
        await _search_image.finish('图片链接错误')
