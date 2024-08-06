import math
import re
import typing
from typing import Sequence

from sqlalchemy import select, insert, delete, update

from essentials.libraries import database
from . import dice, data

basic_property_names = [x["name"] for x in data.TRPG_BASIC_PROPERTIES.values()]
_investigators_key = "investigators"


def get_property_name(key: str) -> str:
    """
    根据属性 key 获取属性名

    :param key: key

    :return: 属性名
    """
    if key in data.TRPG_BASIC_PROPERTIES:
        return data.TRPG_BASIC_PROPERTIES[key]["name"]
    return ""


def get_property_fullname(key: str) -> str:
    """
    根据属性 key 获取属性全名

    :param key: key

    :return: 属性全名
    """
    if key in data.TRPG_BASIC_PROPERTIES:
        return data.TRPG_BASIC_PROPERTIES[key]["fullname"]
    return ""


def get_property_key(name: str) -> str:
    """
    根据属性名获取属性 key

    :param name: 属性名

    :return: 属性 key
    """
    for k, v in data.TRPG_BASIC_PROPERTIES.items():
        if v["name"] == name:
            return k
    return ""


def random_basic_properties() -> dict[str, int]:
    """
    随机生成基础属性

    :return: 基础属性
    """
    ret: dict[str, int] = {}
    for _, v in data.TRPG_ASSET_PATH["basic_properties"].items():
        ret[v["name"]] = dice.dice_expression(v["dice"])[0]
    return ret


def add_investigator(uid: int, investigator: data.Investigator) -> int:
    """
    添加调查员

    不对传入的 investigator 信息做检查

    :param uid: uid
    :param investigator: 调查员属性

    :return: 调查员 id
    """
    with database.get_session().begin() as session:
        investigator.owner_user_id = uid
        session.add(investigator)
        session.commit()
        return investigator.id


def get_investigator(
    uid: int, investigator_id: str = ""
) -> Sequence[data.Investigator]:
    """
    获取人物卡

    :param uid: uid
    :param investigator_id: 人物卡 id

    :return: investigator_id 存在则返回对应调查员，为空则返回所有调查员，不存在则返回空列表
    """
    with database.get_session().begin() as session:
        query = select(data.Investigator).where(
            data.Investigator.owner_user_id.is_(uid)
        )
        if investigator_id:
            query = query.where(data.Investigator.id.is_(investigator_id))
        return session.execute(query).scalars().all()


def set_selected_investigator(
    user_id: int, group_id: str, investigator_id: str
) -> bool:
    """
    设置当前人物卡

    :param user_id: uid
    :param group_id: 群号
    :param investigator_id: 人物卡 id

    :return: 是否成功
    """
    with database.get_session().begin() as session:
        if (
            session.execute(
                select(data.Investigator)
                .where(data.Investigator.owner_user_id.is_(user_id))
                .where(data.Investigator.id.is_(investigator_id))
            ).first()
            is None
        ):
            return False
        if (
            session.execute(
                select(data.PlayerData)
                .where(data.PlayerData.user_id.is_(user_id))
                .where(data.PlayerData.group_id.is_(group_id))
            ).first()
            is None
        ):
            session.execute(
                insert(data.PlayerData).values(
                    user_id=user_id,
                    group_id=group_id,
                    selected_investigator_id=investigator_id,
                )
            )
        else:
            session.execute(
                update(data.PlayerData)
                .where(data.PlayerData.user_id.is_(user_id))
                .where(data.PlayerData.group_id.is_(group_id))
                .values(selected_investigator_id=investigator_id)
            )
        session.commit()
        return True


def get_selected_investigator(user_id: int, group_id: str) -> data.Investigator | None:
    """
    获取当前人物卡

    :param user_id: 用户 id
    :param group_id: 群 id

    :return: 当前人物卡，未设置则返回 None
    """
    with database.get_session().begin() as session:
        selected = session.execute(
            select(data.PlayerData)
            .where(data.PlayerData.user_id.is_(user_id))
            .where(data.PlayerData.group_id.is_(group_id))
        ).scalar_one_or_none()
        if selected is not None:
            return session.execute(
                select(data.Investigator)
                .where(data.Investigator.owner_user_id.is_(user_id))
                .where(data.Investigator.id.is_(selected.selected_investigator_id))
            ).scalar_one_or_none()


def delete_investigator(user_id: int, investigator_id: str) -> bool:
    """
    删除人物卡

    :param user_id: uid
    :param investigator_id: 人物卡 id

    :return: 是否成功
    """
    with database.get_session().begin() as session:
        if (
            session.execute(
                select(data.Investigator)
                .where(data.Investigator.owner_user_id.is_(user_id))
                .where(data.Investigator.id.is_(investigator_id))
            ).first()
            is None
        ):
            return False
        session.execute(
            delete(data.Investigator)
            .where(data.Investigator.owner_user_id.is_(user_id))
            .where(data.Investigator.id.is_(investigator_id))
        )
        session.commit()
        return True


def check_investigator_id(user_id: int, investigator_id: str) -> bool:
    """
    检查调查员 id 是否存在

    :param user_id: 用户 id
    :param investigator_id: 调查员 id

    :return: 是否存在
    """
    with database.get_session().begin() as session:
        return (
            session.execute(
                select(data.Investigator)
                .where(data.Investigator.owner_user_id.is_(user_id))
                .where(data.Investigator.id.is_(investigator_id))
            ).first()
            is not None
        )


def generate_investigator(raw: str) -> data.Investigator:
    """
    生成人物卡，对传入信息不做检查

    :param raw: 原始信息

    :return: 人物卡
    """
    # 初始化人物卡
    investigator = data.Investigator()

    for i in re.split("[,，]", raw):
        k, v = i.split("=")
        k: str = k.strip()
        v: str = v.strip()
        if k == "姓名":
            investigator.name = v
        elif k == "性别":
            investigator.gender = v
        elif k == "年龄":
            investigator.age = int(v)
        elif k == "出生地":
            investigator.birthplace = v
        elif k == "职业":
            investigator.profession = v
        elif k in basic_property_names:
            setattr(investigator, get_property_fullname(k), int(v))
    return investigator


def get_success_rank(value: int, target: int) -> typing.Tuple[int, str]:
    """
    获取成功等级

    :param value: 检定值
    :param target: 目标值

    :return: 成功等级，成功等级描述
    """
    if value == 1:
        return 5, "大成功"
    elif value <= target / 5:
        return 4, "极难成功"
    elif value <= target / 2:
        return 3, "困难成功"
    elif value <= target:
        return 2, "成功"
    elif target >= 50 and value == 100 or target < 50 and value >= 96:
        return 0, "大失败"
    return 1, "失败"


def property_check(
    user_id: int, group_id: str, property_name: str, value: int | None = None
) -> typing.Tuple[str, int, int] | None:
    """
    属性检定

    :param user_id: 用户 id
    :param group_id: 群 id
    :param property_name: 属性名
    :param value: 检定值，为空则随机生成

    :return: 检定结果，检定值，目标值，失败返回 None
    """
    if not value:
        value = dice.simple_dice_expression("d100")
    investigator = get_selected_investigator(user_id, group_id)
    if investigator is not None:
        target: int = getattr(investigator, get_property_fullname(property_name))
        _, check_result = get_success_rank(value, target)
        return check_result, value, target
    return None


def calculate_db_physique(user_id: int, group_id: str) -> typing.Tuple[int, int] | None:
    """
    计算伤害加值和体格

    :param user_id: 用户 id
    :param group_id: 群 id

    :return: 伤害加值, 体格，失败返回 None
    """
    investigator = get_selected_investigator(user_id, group_id)
    if investigator is not None:
        add = investigator.strength + investigator.size
        if add <= 64:
            return -2, -2
        elif add <= 84:
            return -1, -1
        elif add <= 124:
            return 0, 0
        elif add <= 164:
            return dice.simple_dice_expression("1d4"), 1
        elif add <= 204:
            return dice.simple_dice_expression("1d6"), 2
        elif add <= 284:
            return dice.simple_dice_expression("2d6"), 3
        elif add <= 364:
            return dice.simple_dice_expression("3d6"), 4
        elif add <= 444:
            return dice.simple_dice_expression("4d6"), 5
        elif add <= 524:
            return dice.simple_dice_expression("5d6"), 6
    return None


def calculate_hp(user_id: int, group_id: str) -> int | None:
    """
    计算耐久值

    :param user_id: 用户 id
    :param group_id: 群 id

    :return: 耐久值，失败返回 None
    """
    investigator = get_selected_investigator(user_id, group_id)
    if investigator is not None:
        return math.floor((investigator.constitution + investigator.size) / 10)
    return None


def calculate_mov(user_id: int, group_id: str) -> int | None:
    """
    计算移动速度

    :param user_id: 用户 id
    :param group_id: 群 id

    :return: 移动速度，失败返回 None
    """
    investigator = get_selected_investigator(user_id, group_id)
    if investigator is not None:
        # 计算移动速度
        mov = 8
        if (
            investigator.strength < investigator.size
            and investigator.dexterity < investigator.size
        ):
            mov = 7
        elif (
            investigator.strength > investigator.size
            and investigator.dexterity > investigator.size
        ):
            mov = 9
        # 年龄
        if 40 <= investigator.age <= 49:
            mov -= 1
        elif 50 <= investigator.age <= 59:
            mov -= 2
        elif 60 <= investigator.age <= 69:
            mov -= 3
        elif 70 <= investigator.age <= 79:
            mov -= 4
        elif 80 <= investigator.age <= 89:
            mov -= 5
        return mov
    return None


_ = """ investigator example
{
    "name": "xxx",
    "gender": "xxx",
    "age": 18,
    "profession": "xxx",
    "basic_properties": {"str": 20, "con": 30, ...},
    "additional_properties": {"aaa": 20, "bbb": 30},
    "skills": {"aaa": 20, "bbb": 30},
    "status": {"hp": 15, "san": 80}
    "items": {"aaa": ...},
    "extra": {"xxx": ...}
}
"""
