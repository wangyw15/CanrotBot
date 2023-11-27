import json
from datetime import datetime
from pathlib import Path

import nonebot
from sqlalchemy import insert

nonebot.init()

# 前置插件
nonebot.load_plugin("nonebot_plugin_apscheduler")

# 基础插件
essentials_plugins_path = (Path(__file__).parent / "essentials" / "plugins").resolve()
nonebot.load_plugins(str(essentials_plugins_path))

# 普通插件
plugins_path = (Path(__file__).parent / "plugins").resolve()
nonebot.load_plugins(str(plugins_path))

from storage import config, database


def convert_to_datetime(iso_format: str) -> datetime:
    """
    转换为普通时间

    :param iso_format: 时间字符串

    :return: 普通时间
    """
    tmp = datetime.fromisoformat(iso_format)
    return datetime(
        tmp.year, tmp.month, tmp.day, tmp.hour, tmp.minute, tmp.second, tmp.microsecond
    )


# 是否存在数据
data_path = Path(config.canrot_config.canrot_data_path)
if not data_path.exists() or not data_path.is_dir():
    print("无事可做")
    exit(0)


# essentials.libraries.user
from essentials.libraries.user import data as user_data

with open(data_path / "user" / "users.json", encoding="utf-8") as f:
    data = json.load(f)

uid_list = []
for puid, uid in data.items():
    if uid not in uid_list:
        uid_list.append(uid)

with database.get_session().begin() as session:
    session.execute(
        insert(user_data.User).values([{"user_id": uid} for uid in uid_list])
    )
    session.execute(
        insert(user_data.Bind).values(
            [{"platform_user_id": puid, "user_id": uid} for puid, uid in data.items()]
        )
    )


# essentials.libraries.economy
from essentials.libraries.economy import data as economy_data

for i in (data_path / "economy").glob("*.json"):
    with i.open(encoding="utf-8") as f:
        data = json.load(f)
    with database.get_session().begin() as session:
        session.execute(
            insert(economy_data.Account).values(user_id=i.stem, balance=data["balance"])
        )
        session.execute(
            insert(economy_data.Record).values(
                [
                    {
                        "user_id": i.stem,
                        "time": convert_to_datetime(record["time"]),
                        "amount": record["amount"],
                        "balance": record["balance"],
                        "description": record["description"],
                    }
                    for record in data["history"]
                ]
            )
        )


# essentials.plugins.bot_admin
pass


# plugins.arknights
from plugins.arknights import data as arknights_data

for i in (data_path / "arknights").glob("*.json"):
    with i.open(encoding="utf-8") as f:
        data = json.load(f)

    with database.get_session().begin() as session:
        session.execute(
            insert(arknights_data.Statistics).values(
                user_id=i.stem,
                three_stars=data["2"],
                four_stars=data["3"],
                five_stars=data["4"],
                six_stars=data["5"],
                times=data["times"],
                last_six_star=data["last_5"],
            )
        )
        if data["history"]:
            session.execute(
                insert(arknights_data.History).values(
                    [
                        {
                            "user_id": i.stem,
                            "time": convert_to_datetime(record["time"]),
                            "operators": json.dumps(
                                record["operators"], ensure_ascii=False
                            ),
                        }
                        for record in data["history"]
                    ]
                )
            )


# plugins.comment
from plugins.comment import data as comment_data

with open(data_path / "comment" / "anime.json", encoding="utf-8") as f:
    data = json.load(f)
    with database.get_session().begin() as session:
        for title, contents in data.items():
            session.execute(
                insert(comment_data.Comment).values(
                    [
                        {
                            "type": comment_data.CommentType.anime,
                            "time": convert_to_datetime(content["time"]),
                            "title": title,
                            "author": content["uid"],
                            "content": content["comment"],
                            "nickname": content["nickname"],
                        }
                        for content in contents
                    ]
                )
            )


# plugins.muse_dash
from plugins.muse_dash import data as muse_dash_data

for i in (data_path / "muse_dash").glob("*.json"):
    with i.open(encoding="utf-8") as f:
        data = json.load(f)

    with database.get_session().begin() as session:
        session.execute(
            insert(muse_dash_data.MuseDashAccount).values(
                user_id=i.stem, player_name=data["name"], player_id=data["id"]
            )
        )


# plugins.reply
from plugins.reply import data as reply_data

for i in (data_path / "reply").glob("*.json"):
    with i.open(encoding="utf-8") as f:
        data = json.load(f)
    with database.get_session().begin() as session:
        session.execute(
            insert(reply_data.ReplyConfig).values(
                group_id=i.stem, enable=data["enabled"], rate=data["rate"]
            )
        )


# plugins.signin
from plugins.signin import data as signin_data

for i in (data_path / "signin").glob("*.json"):
    with i.open(encoding="utf-8") as f:
        data = json.load(f)
    with database.get_session().begin() as session:
        session.execute(
            insert(signin_data.SigninRecord).values(
                user_id=i.stem,
                time=datetime.strptime(data["last_date"], "%Y-%m-%d"),
                title=data["fortune_title"],
                content=data["fortune_content"],
            )
        )


# plugins.trpg
from plugins.trpg import data as trpg_data

for i in (data_path / "trpg").glob("*.json"):
    with i.open(encoding="utf-8") as f:
        data = json.load(f)
    with database.get_session().begin() as session:
        session.execute(
            insert(trpg_data.Investigator).values(
                [
                    {
                        "owner_user_id": i.stem,
                        "name": v["name"],
                        "age": v["age"],
                        "gender": v["gender"],
                        "profession": v["profession"],
                        "strength": v["basic_properties"]["str"],
                        "constitution": v["basic_properties"]["con"],
                        "dexterity": v["basic_properties"]["dex"],
                        "appearance": v["basic_properties"]["app"],
                        "power": v["basic_properties"]["pow"],
                        "intelligence": v["basic_properties"]["int"],
                        "size": v["basic_properties"]["siz"],
                        "education": v["basic_properties"]["edu"],
                        "luck": v["basic_properties"]["luck"],
                    }
                    for _, v in data["investigators"].items()
                ]
            )
        )
