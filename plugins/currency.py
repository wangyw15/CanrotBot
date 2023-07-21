import re
import typing

import httpx
from nonebot import on_command, on_regex
from nonebot.adapters import Message
from nonebot.params import CommandArg, RegexGroup
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='查汇率',
    description='可以查到工行的汇率，也可以转换汇率',
    usage='查汇率：/<currency|汇率> <币种，中英文皆可>\n汇率转换：100jpy=或者100rmb=jpy',
    config=None
)

_client = httpx.AsyncClient()


async def fetch_currency() -> list[dict[str, str]]:
    resp = await _client.get('https://papi.icbc.com.cn/exchanges/ns/getLatest')
    if resp.status_code == 200:
        data = resp.json()
        if data['message'] == 'success' and data['code'] == 0:
            return data['data']
    return []


# 搜索指定汇率信息
currency_query = on_command('currency', aliases={'汇率'}, block=True)


@currency_query.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        currency_data = await fetch_currency()
        if not currency_data:
            await currency_query.finish('获取汇率失败')
        for item in currency_data:
            if msg.lower() == item['currencyENName'].lower() or msg == item['currencyCHName']:
                await currency_query.finish(f"""
币种：{item['currencyCHName']}({item['currencyENName']})
参考价格：  {item['reference']}
现汇买入价：{item['foreignBuy']}
现钞买入价：{item['cashBuy']}
现汇卖出价：{item['foreignSell']}
现钞卖出价：{item['cashSell']}
发布时间：{item['publishDate']} {item['publishTime']}
单位：人民币/100外币
                """.strip())
        await currency_query.finish('未找到该货币')
    else:
        await currency_query.finish('请输入货币名称')


# 汇率转换
_currency_convert_handler = on_regex(r'^(\d+(?:.\d+)?)([a-zA-Z\u4e00-\u9fa5]+)[=＝]([a-zA-Z\u4e00-\u9fa5]+)$',
                                     flags=re.IGNORECASE, block=True)


@_currency_convert_handler.handle()
async def _(reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]):
    amount: float | int = eval(reg[0].strip())
    currency_from: str = reg[1].strip()
    currency_to: str = reg[2].strip()
    if amount and currency_from and currency_to:
        currency_data = await fetch_currency()
        if not currency_data:
            await _currency_convert_handler.finish('获取汇率失败')
        price_from = ''
        price_to = ''
        name_from = ''
        name_to = ''
        for item in currency_data:
            if currency_from.lower() == item['currencyENName'].lower() or currency_from == item['currencyCHName']:
                price_from = float(item['foreignBuy'])
                name_from = item['currencyCHName']
            elif currency_from.lower() in ['rmb', 'cny'] or currency_from == '人民币':
                price_from = 100
                name_from = '人民币'
            if currency_to.lower() == item['currencyENName'].lower() or currency_to == item['currencyCHName']:
                price_to = float(item['foreignSell'])
                name_to = item['currencyCHName']
            elif currency_to.lower() in ['rmb', 'cny'] or currency_to == '人民币':
                price_to = 100
                name_to = '人民币'
        if price_from and price_to:
            await _currency_convert_handler.finish(
                f'{amount}{name_from}={round(amount * price_from / price_to, 4)}{name_to}')
        await currency_query.finish('未找到该货币')
    else:
        await currency_query.finish('查询格式有误')
