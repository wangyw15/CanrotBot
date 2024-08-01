from typing import Callable

USER1_UID = (1 << 62) + 1
USER2_UID = (1 << 62) + 2


def test_create_economy_tables(db_initialize: Callable) -> None:
    from storage.database import Base
    from essentials.libraries import economy

    db_initialize()

    assert economy.data.Account.__tablename__ in Base.metadata.tables
    assert economy.data.Transaction.__tablename__ in Base.metadata.tables


def test_set_balance_without_record(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(USER1_UID) == 0

    economy.set_balance(USER1_UID, 100)
    assert economy.get_balance(USER1_UID) == 100


def test_earn_positive_amount(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(USER1_UID) == 0

    economy.earn(USER1_UID, 100)
    assert economy.get_balance(USER1_UID) == 100

    economy.earn(USER1_UID, 100)
    assert economy.get_balance(USER1_UID) == 200


def test_earn_negative_amount(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(USER1_UID) == 0

    economy.earn(USER1_UID, 100)
    assert economy.get_balance(USER1_UID) == 100

    economy.earn(USER1_UID, -100)
    assert economy.get_balance(USER1_UID) == 100


def test_pay_positive_amount(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(USER1_UID) == 0

    economy.earn(USER1_UID, 100)
    assert economy.get_balance(USER1_UID) == 100

    economy.pay(USER1_UID, 50)
    assert economy.get_balance(USER1_UID) == 50


def test_pay_negative_amount(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(USER1_UID) == 0

    economy.earn(USER1_UID, 100)
    assert economy.get_balance(USER1_UID) == 100

    economy.pay(USER1_UID, -100)
    assert economy.get_balance(USER1_UID) == 100


def test_transfer_positive_amount(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(USER1_UID) == 0
    assert economy.get_balance(USER2_UID) == 0

    economy.earn(USER1_UID, 100)
    assert economy.get_balance(USER1_UID) == 100

    assert economy.transfer(USER1_UID, USER2_UID, 50)
    assert economy.get_balance(USER1_UID) == 50
    assert economy.get_balance(USER2_UID) == 50


def test_transfer_not_enough_balance(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(USER1_UID) == 0
    assert economy.get_balance(USER2_UID) == 0

    assert not economy.transfer(USER1_UID, USER2_UID, 100)


def test_transfer_negative_amount(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(USER1_UID) == 0
    assert economy.get_balance(USER2_UID) == 0

    assert not economy.transfer(USER1_UID, USER2_UID, -100)
