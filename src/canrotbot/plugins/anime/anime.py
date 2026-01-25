from typing import Any


def generate_message_from_anilist_data(data: dict) -> str:
    # 放送状态
    anime_status = "未知"
    if data["status"] == "FINISHED":
        anime_status = "完结"
    elif data["status"] == "RELEASING":
        anime_status = "更新中"
    elif data["status"] == "NOT_YET_RELEASED":
        anime_status = "待放送"

    # 春夏秋冬季
    anime_time = f"{data['seasonYear']}年"
    if data["season"] == "SPRING":
        anime_time += "春季"
    elif data["season"] == "SUMMER":
        anime_time += "夏季"
    elif data["season"] == "FALL":
        anime_time += "秋季"
    elif data["season"] == "WINTER":
        anime_time += "冬季"

    # 生成消息
    msg = (
        f"标题: {data['title']['native']}\n"
        + f"共 {data['episodes']} 集\n"
        + f"状态: {anime_status}\n"
        + f"时间: {anime_time}\n"
        + f"标签: {', '.join([i['name'] for i in data['tags']])}\n"
    )
    return msg


def generate_message_from_bangumi_calendar(data: list[dict[str, Any]]) -> str:
    msg = ""
    for i in data:
        msg += "----- " + i["weekday"]["cn"] + " -----\n"
        for j in i["items"]:
            name = j["name_cn"] or j["name"]
            if name:
                msg += name + "\n"
        msg += "\n"

    return msg
