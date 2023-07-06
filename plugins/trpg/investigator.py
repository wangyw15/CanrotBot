import re

from essentials.libraries import asset, util
from . import dice, data

_assets = asset.Asset('trpg')
_basic_property_names = [x['name'] for x in _assets['basic_properties'].values()]


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


def set_card(uid: str, card: dict[str], card_id: str = '') -> str:
    """
    添加或修改人物卡，如果 card_id 为空则随机生成

    不对传入的 card 信息做检查

    :param uid: uid
    :param card: 人物卡
    :param card_id: 人物卡 id

    :return: 人物卡 id
    """
    if uid not in data.trpg_data:
        data.trpg_data[uid] = {}
    if 'cards' not in data.trpg_data[uid]:
        data.trpg_data[uid]['cards'] = {}
    if not card_id:
        while True:
            card_id = util.random_str(8)
            if card_id not in data.trpg_data[uid]['cards']:
                break
    data.trpg_data[uid]['cards'][card_id] = card
    data.trpg_data.save()
    return card_id


def get_card(uid: str, card_id: str = '') -> dict[str, dict[str]]:
    """
    获取人物卡

    :param uid: uid
    :param card_id: 人物卡 id

    :return: card_id 存在则返回对应人物卡，为空则返回所有人物卡，不存在则返回空字典
    """
    if uid in data.trpg_data and 'cards' in data.trpg_data[uid]:
        if card_id in data.trpg_data[uid]['cards']:
            return {card_id: data.trpg_data[uid]['cards'][card_id]}
        elif not card_id:
            return data.trpg_data[uid]['cards']
    return {}


def delete_card(uid:str, card_id: str) -> bool:
    """
    删除人物卡

    :param uid: uid
    :param card_id: 人物卡 id
    """
    if uid in data.trpg_data and 'cards' in data.trpg_data[uid]:
        if card_id in data.trpg_data[uid]['cards']:
            del data.trpg_data[uid]['cards'][card_id]
            data.trpg_data.save()
            return True
    return False


def generate_card(raw: str) -> dict[str]:
    """
    生成人物卡

    :param raw: 原始信息

    :return: 人物卡
    """
    # 初始化人物卡
    card: dict[str] = {'basic_properties': {}, 'properties': {}, 'skills': {}, 'items': {}, 'extra': {}}

    for i in re.split('[,，]', raw):
        k, v = i.split('=')
        k: str = k.strip()
        v: str = v.strip()
        if k == '姓名':
            card['name'] = v
        elif k == '性别':
            card['gender'] = v
        elif k == '年龄':
            card['age'] = int(v)
        elif k == '职业':
            card['profession'] = v
        elif k in _basic_property_names:
            card['basic_properties'][get_property_key(k)] = int(v)
        elif v.isdigit():
            card['skills'][k] = int(v)
        else:
            card['items'][k] = v
    if 'name' not in card or 'gender' not in card or 'age' not in card or 'profession' not in card:
        return {}
    if len(card['basic_properties']) != len(_basic_property_names):
        return {}
    return card


_ = ''' card example
{
    "name": "xxx",
    "gender": "xxx",
    "age": 18,
    "profession": "xxx",
    "basic_properties": {"aaa": 20, "bbb": 30},
    "skills": {"aaa": 20, "bbb": 30},
    "properties": {"aaa": 20, "bbb": 30},
    "items": {"aaa": ...},
    "extra": {"xxx": ...}
}
'''
