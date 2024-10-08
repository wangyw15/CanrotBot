from datetime import datetime
from typing import Sequence, cast

from sqlalchemy import select, insert, update, ColumnElement

from .data import Account, Transaction
from .. import database


def _add_transaction(
    uid: int,
    amount: float,
    balance: float,
    description: str = "",
    time: datetime | None = None,
) -> None:
    """
    添加交易记录

    :param uid: uid
    :param amount: 交易金额
    :param balance: 交易后余额
    :param description: 交易描述，默认为空
    :param time: 交易时间，默认为当前时间
    """
    if not time:
        time = datetime.now()
    with database.get_session().begin() as session:
        if (
            session.execute(
                select(data.Account).where(
                    cast(ColumnElement[bool], data.Account.user_id == uid)
                )
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


def get_balance(uid: int) -> float:
    """
    获取用户余额

    :param uid: uid

    :return: 余额
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(data.Account).where(
                cast(ColumnElement[bool], data.Account.user_id == uid)
            )
        ).scalar_one_or_none()
        if result is None:
            return 0.0
        return result.balance


def set_balance(uid: int, balance: float) -> None:
    """
    设置用户余额

    :param uid: uid
    :param balance: 余额
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(data.Account).where(
                cast(ColumnElement[bool], data.Account.user_id == uid)
            )
        ).scalar_one_or_none()
        if result is None:
            session.execute(insert(data.Account).values(user_id=uid, balance=balance))
        else:
            session.execute(
                update(data.Account)
                .where(cast(ColumnElement[bool], data.Account.user_id == uid))
                .values(balance=balance)
            )
        session.commit()


def pay(uid: int, amount: float, description: str = "pay") -> bool:
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
    _add_transaction(uid, -amount, get_balance(uid) - amount, description)
    set_balance(uid, get_balance(uid) - amount)
    return True


def earn(uid: int, amount: float, description: str = "earn") -> None:
    """
    入账

    :param uid: uid
    :param amount: 入账金额
    :param description: 入账描述
    """
    if amount < 0:
        return
    _add_transaction(uid, amount, get_balance(uid) + amount, description)
    set_balance(uid, get_balance(uid) + amount)


def transfer(from_uid: int, to_uid: int, amount: float, description: str = "") -> bool:
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


def get_transactions(uid: int, limit: int | None = None) -> Sequence[Transaction]:
    """
    获取交易记录

    :param uid: uid
    :param limit: 交易记录数量，None为全部，默认为全部

    :return: 交易记录
    """
    with database.get_session().begin() as session:
        records = (
            session.execute(
                select(data.Transaction)
                .where(cast(ColumnElement[bool], data.Transaction.user_id == uid))
                .order_by(data.Transaction.time.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
        session.expunge_all()
        return records
