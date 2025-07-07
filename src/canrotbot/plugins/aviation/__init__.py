from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from . import weather

__plugin_meta__ = PluginMetadata(
    name="模拟飞行工具",
    description="查模拟飞行信息的小玩意",
    usage="/matar <ICAO代码/用逗号分隔的列表>\n/taf<ICAO代码/用逗号分隔的列表>",
    config=None,
)

# METAR report
metar_matcher = on_command("metar", block=True)


@metar_matcher.handle()
async def _(args: Message = CommandArg()):
    if icao_codes := args.extract_plain_text():
        icao_codes = icao_codes.replace("，", ",").replace(",", " ").split()
        if result := await weather.metar(icao_codes):
            msg = ""
            for metar in result:
                msg += metar["icaoId"] + "(" + metar["name"] + ")\n"
                msg += metar["rawOb"] + "\n\n"
            await metar_matcher.finish(msg.strip())
        else:
            await metar_matcher.finish("METAR信息获取失败")
    else:
        await metar_matcher.finish("请输入机场ICAO代码")


# TAF report
taf_matcher = on_command("taf", block=True)


@taf_matcher.handle()
async def _(args: Message = CommandArg()):
    if icao_codes := args.extract_plain_text():
        icao_codes = icao_codes.replace("，", ",").replace(",", " ").split()
        if result := await weather.taf(icao_codes):
            msg = ""
            for taf in result:
                msg += taf["icaoId"] + "(" + taf["name"] + ")\n"
                msg += taf["rawTAF"] + "\n\n"
            await taf_matcher.finish(msg.strip())
        else:
            await taf_matcher.finish("TAF信息获取失败")
    else:
        await taf_matcher.finish("请输入机场ICAO代码")
