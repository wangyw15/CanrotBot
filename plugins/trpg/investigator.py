from . import dice, data
from essentials.libraries import asset, util

_assets = asset.Asset('trpg')


def random_basic_properties() -> dict[str, int]:
    """
    随机生成基础属性

    :return: 基础属性
    """
    ret: dict[str, int] = {}
    for name, expr in _assets['basic_properties'].items():
        ret[name] = dice.dice_expression(expr)[0]
    return ret


def set_card(uid: str, card: dict[str], card_id: str = ''):
    """
    添加或修改人物卡，如果 card_id 为空则随机生成

    不对传入的 card 信息做检查

    :param uid: uid
    :param card: 人物卡
    :param card_id: 人物卡 id
    """
    if not card_id:
        while True:
            card_id = util.random_str(8)
            if card_id not in data.trpg_data[uid]['cards']:
                break
    if 'cards' not in data.trpg_data[uid]:
        data.trpg_data[uid]['cards'] = {}
    data.trpg_data[uid]['cards'][card_id] = card
    data.trpg_data.save()


_ = ''' card example
{
    "name": "xxx",
    "gender": "xxx",
    "age": 18,
    "profession": "xxx",
    "properties": [{"aaa": 20, "bbb": 30}],
    "skills": [{"aaa": 20, "bbb": 30}],
    "items": [{...}],
    "extra": {"xxx": ...}
}
'''
