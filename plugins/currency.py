from nonebot import on_command, on_regex
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.typing import T_State
import requests

from ..data import add_help_message

add_help_message('currency', '汇率')

def fetch_currency() -> list[dict[str, str]]:
    resp = requests.get('https://papi.icbc.com.cn/exchanges/ns/getLatest')
    if resp.status_code == 200:
        data = resp.json()
        if data['message'] == 'success' and data['code'] == 0:
            return data['data']
    return []

# curreny search
currency_query = on_command('currency', aliases={'汇率'}, block=True)
@currency_query.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        currency_data = fetch_currency()
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

# currency convert
currency_convert = on_regex(r'(^\d+(?:.\d+)?)(\S+)=?$', block=True)
@currency_convert.handle()
async def _(state: T_State):
    amount = float(state['_matched_groups'][0])
    currency = state['_matched_groups'][1]
    if amount and currency:
        currency_data = fetch_currency()
        if not currency_data:
            await currency_convert.finish('获取汇率失败')
        for item in currency_data:
            if currency.lower() == item['currencyENName'].lower() or currency == item['currencyCHName']:
                price = float(item['foreignSell'])
                await currency_convert.finish(f"{amount}{item['currencyCHName']} = {amount/100*price}人民币")
        await currency_query.finish('未找到该货币')
    else:
        await currency_query.finish('查询格式有误')
