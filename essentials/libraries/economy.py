from datetime import datetime

import storage

_economy_data = storage.PersistentData[dict[str]]('economy')


def _add_history(uid: str, amount: float, balance: float, description: str = '', time: datetime | None = None):
    if not time:
        time = datetime.now()
    if uid not in _economy_data:
        _economy_data[uid] = {}
    if 'history' not in _economy_data[uid]:
        _economy_data[uid]['history'] = []
    _economy_data[uid]['history'].append({
        'time': time.astimezone().isoformat(),
        'amount': amount,
        'balance': balance,
        'description': description
    })


def get_balance(uid: str) -> float:
    """
    获取用户余额

    :param uid: uid

    :return: 余额
    """
    if uid not in _economy_data:
        return 0.0
    if 'balance' not in _economy_data[uid]:
        return 0.0
    return _economy_data[uid]['balance']


def set_balance(uid: str, balance: float):
    """set the balance of a user"""
    if uid not in _economy_data:
        _economy_data[uid] = {}
    _economy_data[uid]['balance'] = balance
    _economy_data.save()


def pay(uid: str, amount: float, description: str = 'pay') -> bool:
    """
    出账

    :param uid: uid
    :param amount: 出账金额
    :param description: 出账描述

    :return: 是否成功出账
    """
    if amount < 0:
        return False
    if get_balance(uid) < amount:
        return False
    _add_history(uid, -amount, get_balance(uid) - amount, description)
    set_balance(uid, get_balance(uid) - amount)
    return True


def earn(uid: str, amount: float, description: str = 'earn'):
    """
    入账

    :param uid: uid
    :param amount: 入账金额
    :param description: 入账描述
    """
    if amount < 0:
        return
    _add_history(uid, amount, get_balance(uid) + amount, description)
    set_balance(uid, get_balance(uid) + amount)


def transfer(from_uid: str, to_uid: str, amount: float, description: str = '') -> bool:
    """
    转账

    :param from_uid: 转出的uid
    :param to_uid: 转入的uid
    :param amount: 转账金额
    :param description: 转账描述

    :return: 是否成功转账
    """
    if not description:
        description = f'{from_uid} transfer to {to_uid}'
    if amount < 0:
        return False
    if not pay(from_uid, amount, description):
        return False
    earn(to_uid, amount, description)
    return True


def get_history(uid: str) -> list[dict[str]]:
    """
    查询交易记录

    :param uid: uid

    :return: 交易记录
    """
    if uid not in _economy_data:
        return []
    if 'history' not in _economy_data[uid]:
        return []
    return _economy_data[uid]['history']
