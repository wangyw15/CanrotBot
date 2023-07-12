import re
import typing

from essentials.libraries import asset, util
from . import dice, data

_assets = asset.Asset('trpg')
basic_property_names = [x['name'] for x in _assets['basic_properties'].values()]
_investigators_key = 'investigators'


def get_property_name(key: str) -> str:
    """
    根据属性 key 获取属性名

    :param key: key

    :return: 属性名
    """
    if key in _assets['basic_properties']:
        return _assets['basic_properties'][key]['name']
    return ''


def get_property_key(name: str) -> str:
    """
    根据属性名获取属性 key

    :param name: 属性名

    :return: 属性 key
    """
    for k, v in _assets['basic_properties'].items():
        if v['name'] == name:
            return k
    return ''


def random_basic_properties() -> dict[str, int]:
    """
    随机生成基础属性

    :return: 基础属性
    """
    ret: dict[str, int] = {}
    for _, v in _assets['basic_properties'].items():
        ret[v['name']] = dice.dice_expression(v['dice'])[0]
    return ret


def set_investigator(uid: str, investigator: dict[str], investigator_id: str = '') -> str:
    """
    添加或修改人物卡，如果 investigator_id 为空则随机生成

    不对传入的 investigator 信息做检查

    :param uid: uid
    :param investigator: 人物卡
    :param investigator_id: 人物卡 id

    :return: 人物卡 id
    """
    if uid not in data.trpg_data:
        data.trpg_data[uid] = {}
    if _investigators_key not in data.trpg_data[uid]:
        data.trpg_data[uid][_investigators_key] = {}
    if not investigator_id:
        while True:
            investigator_id = util.random_str(8)
            if investigator_id not in data.trpg_data[uid][_investigators_key]:
                break
    data.trpg_data[uid][_investigators_key][investigator_id] = investigator
    data.trpg_data.save()
    return investigator_id


def get_investigator(uid: str, investigator_id: str = '') -> dict[str, dict[str]]:
    """
    获取人物卡

    :param uid: uid
    :param investigator_id: 人物卡 id

    :return: investigator_id 存在则返回对应人物卡，为空则返回所有人物卡，不存在则返回空字典
    """
    if uid in data.trpg_data and _investigators_key in data.trpg_data[uid]:
        if investigator_id in data.trpg_data[uid][_investigators_key]:
            return {investigator_id: data.trpg_data[uid][_investigators_key][investigator_id]}
        elif not investigator_id:
            return data.trpg_data[uid][_investigators_key]
    return {}


def set_selected_investigator(uid: str, investigator_id: str) -> bool:
    """
    设置当前人物卡

    :param uid: uid
    :param investigator_id: 人物卡 id

    :return: 是否成功
    """
    if uid not in data.trpg_data or investigator_id not in data.trpg_data[uid][_investigators_key]:
        return False
    data.trpg_data[uid]['selected_investigator'] = investigator_id
    data.trpg_data.save()
    return True


def get_selected_investigator(uid: str) -> dict[str]:
    """
    获取当前人物卡

    :param uid: uid

    :return: 当前人物卡，未设置则返回空字典
    """
    if uid in data.trpg_data and 'selected_investigator' in data.trpg_data[uid] \
            and data.trpg_data[uid]['selected_investigator']:
        iid = data.trpg_data[uid]['selected_investigator']
        return {iid: data.trpg_data[uid][_investigators_key][iid]}
    return {}


def delete_investigator(uid: str, investigator_id: str) -> bool:
    """
    删除人物卡

    :param uid: uid
    :param investigator_id: 人物卡 id
    """
    if uid in data.trpg_data and _investigators_key in data.trpg_data[uid]:
        if investigator_id in data.trpg_data[uid][_investigators_key]:
            del data.trpg_data[uid][_investigators_key][investigator_id]
            data.trpg_data.save()
            return True
    return False


def check_investigator_id(uid: str, investigator_id: str) -> bool:
    """
    检查人物卡 id 是否存在

    :param uid: uid
    :param investigator_id: 人物卡 id

    :return: 是否存在
    """
    if uid in data.trpg_data and _investigators_key in data.trpg_data[uid]:
        return investigator_id in data.trpg_data[uid][_investigators_key]
    return False


def generate_investigator(raw: str) -> dict[str]:
    """
    生成人物卡

    :param raw: 原始信息

    :return: 人物卡
    """
    # 初始化人物卡
    investigator: dict[str] = {
        'basic_properties': {},
        'additional_properties': {},
        'skills': {},
        'status': {},
        'items': {},
        'extra': {}
    }

    for i in re.split('[,，]', raw):
        k, v = i.split('=')
        k: str = k.strip()
        v: str = v.strip()
        if k == '姓名':
            investigator['name'] = v
        elif k == '性别':
            investigator['gender'] = v
        elif k == '年龄':
            investigator['age'] = int(v)
        elif k == '职业':
            investigator['profession'] = v
        elif k in basic_property_names:
            investigator['basic_properties'][get_property_key(k)] = int(v)
        elif v.isdigit():
            investigator['skills'][k] = int(v)
        else:
            investigator['items'][k] = v
    if 'name' not in investigator or 'gender' not in investigator \
            or 'age' not in investigator or 'profession' not in investigator:
        return {}
    if len(investigator['basic_properties']) != len(basic_property_names):
        return {}
    return investigator


def property_check(uid: str, property_name: str, value: int | None = None) -> typing.Tuple[str, int, int]:
    """
    属性检定

    :param uid: uid
    :param property_name: 属性名
    :param value: 检定值，为空则随机生成

    :return: 检定结果，目标值，检定值
    """
    if not value:
        value = dice.simple_dice_expression('d100')
    if uid in data.trpg_data and _investigators_key in data.trpg_data[uid]:
        iid, card = get_selected_investigator(uid).popitem()
        target = card['basic_properties'][get_property_key(property_name)]
        check_result = '失败'
        if value == 1:
            check_result = '大成功'
        elif value <= target / 5:
            check_result = '极难成功'
        elif value <= target / 2:
            check_result = '困难成功'
        elif value <= target:
            check_result = '成功'
        elif target >= 50 and value == 100 or target < 50 and value >= 96:
            check_result = '大失败'
        return check_result, target, value


_ = ''' investigator example
{
    "name": "xxx",
    "gender": "xxx",
    "age": 18,
    "profession": "xxx",
    "basic_properties": {"aaa": 20, "bbb": 30},
    "additional_properties": {"aaa": 20, "bbb": 30},
    "skills": {"aaa": 20, "bbb": 30},
    "status": {"hp": 15, "san": 80}
    "items": {"aaa": ...},
    "extra": {"xxx": ...}
}
'''
