from nonebot import on_command, on_regex
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
import re
import httpx

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


# currency search
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


# currency convert from foreign to rmb
currency_convert_to_rmb = on_regex(r'^([\d()\-+*/.]+)([a-zA-Z\u4e00-\u9fa5]+)=$', block=True)
@currency_convert_to_rmb.handle()
async def _(state: T_State):
    amount: float | int = eval(state['_matched_groups'][0].strip())
    currency: str = state['_matched_groups'][1].strip()
    if amount and currency:
        currency_data = await fetch_currency()
        if not currency_data:
            await currency_convert_to_rmb.finish('获取汇率失败')
        for item in currency_data:
            if currency.lower() == item['currencyENName'].lower() or currency == item['currencyCHName']:
                price = float(item['foreignSell'])
                await currency_convert_to_rmb.finish(
                    f"{amount}{item['currencyCHName']} = {round(amount / 100 * price, 4)}人民币")
        await currency_query.finish('未找到该货币')
    else:
        await currency_query.finish('查询格式有误')


# currency convert from rmb to foreign
currency_convert_to_foreign = on_regex(r'^([\d()\-+*/.]+)(?:rmb|人民币|￥)=(?:[?？]|多少)?([a-zA-Z\u4e00-\u9fa5]+)$',
                                       flags=re.IGNORECASE, block=True)
@currency_convert_to_foreign.handle()
async def _(state: T_State):
    amount: float | int = eval(state['_matched_groups'][0].strip())
    currency: str = state['_matched_groups'][1].strip()
    if amount and currency:
        currency_data = await fetch_currency()
        if not currency_data:
            await currency_convert_to_foreign.finish('获取汇率失败')
        for item in currency_data:
            if currency.lower() == item['currencyENName'].lower() or currency == item['currencyCHName']:
                price = float(item['foreignSell'])
                await currency_convert_to_foreign.finish(
                    f"{amount}人民币 = {round(amount * 100 / price, 4)}{item['currencyCHName']}")
        await currency_query.finish('未找到该货币')
    else:
        await currency_query.finish('查询格式有误')
