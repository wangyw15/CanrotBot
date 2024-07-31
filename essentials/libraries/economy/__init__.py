from datetime import datetime

from sqlalchemy import select, insert, update

from storage import database
from . import data
from .data import Account, Transaction


def _add_history(
    uid: str,
    amount: float,
    balance: float,
    description: str = "",
    time: datetime | None = None,
) -> None:
    if not time:
        time = datetime.now()
    with database.get_session().begin() as session:
        if (
            session.execute(
                select(data.Account).where(data.Account.user_id == uid)  # type: ignore
            ).first()
            is None
        ):
            session.execute(insert(data.Account).values(user_id=uid))
        session.execute(
            insert(data.Transaction).values(
                user_id=uid,
                time=time,
                amount=amount,
                balance=balance,
                description=description,
            )
        )
        session.commit()


def get_balance(uid: str) -> float:
    """
    获取用户余额

    :param uid: uid

    :return: 余额
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(data.Account).where(data.Account.user_id == uid)  # type: ignore
        ).scalar_one_or_none()
        if result is None:
            return 0.0
        return result.balance


def set_balance(uid: str, balance: float) -> None:
    """
    设置用户余额

    :param uid: uid
    :param balance: 余额
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(data.Account).where(data.Account.user_id == uid)  # type: ignore
        ).scalar_one_or_none()
        if result is None:
            session.execute(insert(data.Account).values(user_id=uid, balance=balance))
        else:
            session.execute(
                update(data.Account)
                .where(data.Account.user_id == uid)  # type: ignore
                .values(balance=balance)
            )
        session.commit()


def pay(uid: str, amount: float, description: str = "pay") -> bool:
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


def earn(uid: str, amount: float, description: str = "earn"):
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


def transfer(from_uid: str, to_uid: str, amount: float, description: str = "") -> bool:
    """
    转账

    :param from_uid: 转出的uid
    :param to_uid: 转入的uid
    :param amount: 转账金额
    :param description: 转账描述

    :return: 是否成功转账
    """
    if not description:
        description = f"{from_uid} transfer to {to_uid}"
    if amount < 0:
        return False
    if not pay(from_uid, amount, description):
        return False
    earn(to_uid, amount, description)
    return True
