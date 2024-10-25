from nonebot_plugin_alconna import UniMessage, Image, Text

from canrotbot.essentials.libraries.network import fetch_json_data


async def fetch_app_info(
    appid: str, steam_lang: str = "zh-cn", steam_region="cn"
) -> dict | None:
    return await fetch_json_data(
        f"https://store.steampowered.com/api/appdetails/?appids={appid}&l={steam_lang}&cc={steam_region}",
        headers={"Accept-Language": steam_lang},
    )


async def generate_message(app_info: dict, with_url=True) -> UniMessage:
    header_img: str = app_info["header_image"]
    bg_img: str = app_info["background_raw"]

    name: str = app_info["name"]
    appid: int = app_info["steam_appid"]
    desc: str = app_info["short_description"]
    coming_soon: bool = app_info["release_date"]["coming_soon"]
    release_date: str = app_info["release_date"]["date"]
    developers: list[str] = app_info["developers"]
    publishers: list[str] = app_info["publishers"]
    genres: list[str] = [x["description"] for x in app_info["genres"]]
    categories: list[str] = [x["description"] for x in app_info["categories"]]
    initial_price: str = app_info["price_overview"]["initial_formatted"]
    final_price: str = app_info["price_overview"]["final_formatted"]
    discount_percentage: int = app_info["price_overview"]["discount_percent"]

    txt_msg = f"""
名称: {name}
发布时间: {'待发售' if coming_soon else release_date}
开发商: {', '.join(developers)}
发行商: {', '.join(publishers)}
类型: {', '.join(genres)}
分类: {', '.join(categories)}
简介: {desc}
    """.strip()

    if discount_percentage != 0:
        txt_msg += f"\n原价: {initial_price}\n现价: {final_price}\n折扣: {discount_percentage}%"
    else:
        txt_msg += f"\n价格: {final_price}"

    if with_url:
        txt_msg += f"\n链接: https://store.steampowered.com/app/{appid}"

    txt_msg = f"\n{txt_msg}\n"

    ret = UniMessage()
    ret.append(Image(url=header_img))
    ret.append(Text(txt_msg))
    ret.append(Image(url=bg_img))
    return ret
