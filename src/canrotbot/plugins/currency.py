import re
import typing

import httpx
from nonebot import on_command, on_regex, logger
from nonebot.adapters import Message
from nonebot.params import CommandArg, RegexGroup
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="查汇率",
    description="可以查到工行的汇率，也可以转换汇率",
    usage="查汇率：/<currency|汇率> <币种，中英文皆可>\n汇率转换：[100]jpy[cny]，支持加减乘除",
    config=None,
)

_client = httpx.AsyncClient()


async def fetch_currency() -> list[dict[str, str]]:
    resp = await _client.get("http://papi.icbc.com.cn/exchanges/ns/getLatest")
    if resp.status_code == 200:
        data = resp.json()
        if data["message"] == "success" and data["code"] == 0:
            return data["data"]
    return []


# 搜索指定汇率信息
currency_query_handler = on_command("currency", aliases={"汇率"}, block=True)


@currency_query_handler.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        currency_data = await fetch_currency()
        if not currency_data:
            await currency_query_handler.finish("获取汇率失败")
        for item in currency_data:
            if (
                msg.lower() == item["currencyENName"].lower()
                or msg == item["currencyCHName"]
            ):
                await currency_query_handler.finish(
                    f"""
币种：{item['currencyCHName']}({item['currencyENName']})
参考价格：  {item['reference']}
现汇买入价：{item['foreignBuy']}
现钞买入价：{item['cashBuy']}
现汇卖出价：{item['foreignSell']}
现钞卖出价：{item['cashSell']}
发布时间：{item['publishDate']} {item['publishTime']}
单位：人民币/100外币
                """.strip()
                )
        await currency_query_handler.finish("未找到该货币")
    else:
        await currency_query_handler.finish("请输入货币名称")


# 汇率转换
currency_convert_handler = on_regex(
    r"^([\d()\-+*/.]+)?([a-zA-Z]{3})([a-zA-Z]{3})?$",
    flags=re.IGNORECASE,
    block=True,
)


@currency_convert_handler.handle()
async def _(group: typing.Annotated[tuple, RegexGroup()]):
    currency_convert_handler.block = True

    # 处理数据
    amount: float = 100.0
    currency_from: str = group[1]
    currency_to = "cny"
    if group[0]:
        amount: float = float(eval(group[0]))
    if group[2]:
        currency_to = group[2]

    # 获取汇率数据
    currency_data = await fetch_currency()
    if not currency_data:
        logger.warning("获取汇率失败")
        await currency_convert_handler.finish()

    price_from = 0.0
    price_to = 0.0
    name_from = ""
    name_to = ""
    for item in currency_data:
        # 源货币
        if currency_from.lower() == item["currencyENName"].lower():
            price_from = float(item["foreignBuy"])
            name_from = item["currencyCHName"]
        elif currency_from.lower() in ["rmb", "cny"]:
            price_from = 100
            name_from = "人民币"

        # 目标货币
        if currency_to.lower() == item["currencyENName"].lower():
            price_to = float(item["foreignSell"])
            name_to = item["currencyCHName"]
        elif currency_to.lower() in ["rmb", "cny"]:
            price_to = 100
            name_to = "人民币"

    # 计算结果
    if price_from and price_to:
        await currency_convert_handler.finish(
            "{:.4f}{}={:.4f}{}".format(
                amount, name_from, amount * price_from / price_to, name_to
            )
        )

    # 错误处理
    if not price_from:
        logger.warning("未找到货币: {} 可能是误触发".format(currency_from))
    if not price_to:
        logger.warning("未找到货币: {} 可能是误触发".format(currency_to))

    # 由于触发方式特殊，因此不做block，可由其他响应器继续处理
    currency_convert_handler.block = False
    await currency_convert_handler.finish()
