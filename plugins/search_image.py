from nonebot import on_command, get_driver
from nonebot.params import CommandArg, Arg
from nonebot.adapters import Bot, Event, Message
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from pydantic import BaseModel, validator
import httpx

from ..universal_adapters import is_onebot_v11, is_onebot_v12, is_console, ob11, ob12

__plugin_meta__ = PluginMetadata(
    name='识图',
    description='通过 SauceNAO.com 或者 trace.moe 识图，目前仅支持QQ直接发送图片搜索',
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

def generate_cq_message_from_saucenao_result(result: dict) -> Message:
    msg = ''

    # limit
    if 'header' in result:
        msg += '搜图次数限制: \n'
        header: dict = result['header']
        if 'long_remaining' in header:
            if header['long_remaining'] < 1:
                return '今日搜索次数已用完'
            msg += f'今日剩余（每日重置）: {header["long_remaining"]}\n'
        if 'short_remaining' in header:
            if header['short_remaining'] < 1:
                return '30秒内搜索次数已用完'
            msg += f'当前剩余（半分钟重置）: {header["short_remaining"]}\n'

    # results
    msg += '搜图结果: \n'
    results: list[dict] = result['results']
    for result in results:
        # split line
        msg += '--------------------\n'

        header: dict = result['header']
        data: dict = result['data']

        # similarity
        msg += '相似度: ' + header['similarity'] + '\n'

        # thumbnail
        if 'thumbnail' in header:
            msg += '缩略图: \n'
            msg += f'[CQ:image,file={header["thumbnail"]}]\n'
        
        # video
        if 'est_time' in data:
            # title prompt
            if 'anidb_aid' in data or 'mal_id' in data or 'anilist_id' in data:
                # anime data
                msg += '动漫: '
            elif 'imdb_id' in data:
                # imdb data
                msg += '剧集: '
            # title
            if 'source' in data:
                msg += data['source']
            # year
            if 'year' in data:
                msg += f' ({data["year"]}年)'
            msg += '\n'
            if 'jp_name' in data:
                msg += f'日文名: {data["jp_name"]}\n'
            if 'eng_name' in data:
                msg += f'英文名: {data["eng_name"]}\n'
            # episode
            if 'part' in data and data['part']:
                msg += f'集数: {data["part"]}\n'
            # est time
            if 'est_time' in data:
                msg += f'时间: {data["est_time"]}\n'
            # urls
            if 'ext_urls' in data:
                msg += '链接: \n'
                for url in data['ext_urls']:
                    msg += url + '\n'
            continue
        
        # pixiv
        if 'pixiv_id' in data:
            # title
            msg += 'Pixiv: '
            if 'title' in data:
                msg += data['title']
            msg += '\n'
            # author name
            if 'member_name' in data:
                msg += f'作者: {data["member_name"]}\n'
            # artwork id
            if 'pixiv_id' in data:
                msg += f'图片链接: \nhttps://www.pixiv.net/artworks/{data["pixiv_id"]}\n'
            # author id
            if 'member_id' in data:
                msg += f'作者链接: \nhttps://www.pixiv.net/users/{data["member_id"]}\n'
            continue
        
        # patreon
        if 'service' in data and data['service'] == 'patreon':
            msg += 'Patreon: '
            if 'title' in data:
                msg += data['title']
            msg += '\n'
            if 'user_name' in data:
                msg += f'作者: {data["user_name"]}\n'
            if 'id' in data:
                msg += f'作品链接: https://www.patreon.com/posts/{data["id"]}\n'
            if 'user_id' in data:
                msg += f'作者链接: https://www.patreon.com/user?u={data["user_id"]}\n'
            continue
        
        # deviant art
        if 'da_id' in data:
            msg += 'DeviantArt: '
            if 'title' in data:
                msg += data['title']
            msg += '\n'
            # author name
            if 'author_name' in data:
                msg += f'作者: {data["author_name"]}\n'
            # artwork page
            msg += f'图片链接: https://deviantart.com/view/{data["da_id"]}\n'
            # author home page
            if 'author_url' in data:
                msg += f'作者链接: {data["author_url"]}\n'
            continue

        # fur affinity
        if 'fa_id' in data:
            msg += 'Fur Affinity: '
            if 'title' in data:
                msg += data['title']
            msg += '\n'
            # author name
            if 'author_name' in data:
                msg += f'作者: {data["author_name"]}\n'
            # artwork page
            msg += f'图片链接: https://www.furaffinity.net/view/{data["fa_id"]}\n'
            # author home page
            if 'author_url' in data:
                msg += f'作者链接: {data["author_url"]}\n'
            continue

        # art station
        if 'as_project' in data:
            msg += 'Art Station: '
            if 'title' in data:
                msg += data['title']
            msg += '\n'
            # author name
            if 'author_name' in data:
                msg += f'作者: {data["author_name"]}\n'
            # artwork page
            msg += f'图片链接: https://www.artstation.com/artwork/{data["as_project"]}\n'
            # author home page
            if 'author_url' in data:
                msg += f'作者链接: {data["author_url"]}\n'
            continue

        # manga
        if 'type' in data and data['type'] == 'Manga':
            msg += '漫画: '
            if 'source' in data:
                msg += data['source']
            msg += '\n'
            if 'part' in data:
                msg += f'话数: {data["part"]}\n'
            if 'ext_urls' in data:
                msg += '链接: \n'
                for url in data['ext_urls']:
                    msg += url + '\n'
            continue

        # general information
        # title
        if 'title' in data:
            msg += f'名称: {data["title"]}\n'
        elif 'source' in data:
            msg += f'名称: {data["source"]}\n'
        if 'eng_name' in data:
            msg += f'英文名: {data["eng_name"]}\n'
        if 'jp_name' in data:
            msg += f'日文名: {data["jp_name"]}\n'
        
        # author
        if 'creator_name' in data and data['creator_name']:
            msg += f'作者: {data["creator_name"]}'
            if 'creator' in data and data['creator']:
                if isinstance(data['creator'], str):
                    msg += f' ({data["creator"]})'
            msg += '\n'
        elif 'creator_name' in data and isinstance(data['creator'], list[str]):
            msg += ' ('
            for creator in data['creator']:
                msg += creator + ', '
            msg += ')'
        if 'author_name' in data and data['author_name']:
            msg += f'作者: {data["author_name"]}\n'
        if 'author_url' in data and data['author_url']:
            msg += f'作者链接: {data["author_url"]}\n'

        # urls
        if 'ext_urls' in data:
            msg += '链接: \n'
            for url in data['ext_urls']:
                msg += url + '\n'
    return msg

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
    
    if is_onebot_v11(bot) or is_onebot_v12(bot):
        await _search_image.send('请发送图片或图片链接')
    else:
        await _search_image.send('请发送图片链接')

@_search_image.got('image')
async def _(state: T_State, bot: Bot, event: Event, image: Message = Arg()):
    # get img url
    img_url: str = ''
    if is_onebot_v11(bot) or is_onebot_v12(bot):
        if image[0].type == 'image':
            img_url = image[0].data['url']
        elif image[0].type == 'text':
            img_url = image[0].data['text']
        else:
            await _search_image.finish('不是图片或者链接，停止搜图')
    else:
        img_url = image.extract_plain_text()
        if (not img_url) or (not (img_url.startswith('https://') or img_url.startswith('http://'))):
            await _search_image.finish('不是链接，停止搜图')
    img_url = img_url.strip()
    
    # search
    if img_url:
        api: str = state['SEARCH_IMAGE_API']
        if api == 'saucenao':
            search_resp = await search_image_from_saucenao(img_url)
            if search_resp:
                msg = generate_cq_message_from_saucenao_result(search_resp)
                if is_onebot_v11(bot):
                    await _search_image.finish(ob11.Message(msg))
                elif is_onebot_v12(bot):
                    await _search_image.finish(ob12.Message(msg))
                else:
                    await _search_image.finish(msg)
            else:
                await _search_image.finish('搜索失败')
    else:
        await _search_image.finish('图片链接错误')
