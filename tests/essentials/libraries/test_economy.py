from typing import Callable

TEST_UID1 = (1 << 62) + 1
TEST_UID2 = (1 << 62) + 2


def test_create_economy_tables(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries.database import Base
    from canrotbot.essentials.libraries import economy

    db_initialize()

    assert economy.data.Account.__tablename__ in Base.metadata.tables
    assert economy.data.Transaction.__tablename__ in Base.metadata.tables


def test_set_balance_without_record(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(TEST_UID1) == 0

    economy.set_balance(TEST_UID1, 100)
    assert economy.get_balance(TEST_UID1) == 100


def test_earn_positive_amount(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(TEST_UID1) == 0

    economy.earn(TEST_UID1, 100)
    assert economy.get_balance(TEST_UID1) == 100

    economy.earn(TEST_UID1, 100)
    assert economy.get_balance(TEST_UID1) == 200


def test_earn_negative_amount(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(TEST_UID1) == 0

    economy.earn(TEST_UID1, 100)
    assert economy.get_balance(TEST_UID1) == 100

    economy.earn(TEST_UID1, -100)
    assert economy.get_balance(TEST_UID1) == 100


def test_pay_positive_amount(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(TEST_UID1) == 0

    economy.earn(TEST_UID1, 100)
    assert economy.get_balance(TEST_UID1) == 100

    economy.pay(TEST_UID1, 50)
    assert economy.get_balance(TEST_UID1) == 50


def test_pay_negative_amount(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(TEST_UID1) == 0

    economy.earn(TEST_UID1, 100)
    assert economy.get_balance(TEST_UID1) == 100

    economy.pay(TEST_UID1, -100)
    assert economy.get_balance(TEST_UID1) == 100


def test_transfer_positive_amount(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(TEST_UID1) == 0
    assert economy.get_balance(TEST_UID2) == 0

    economy.earn(TEST_UID1, 100)
    assert economy.get_balance(TEST_UID1) == 100

    assert economy.transfer(TEST_UID1, TEST_UID2, 50)
    assert economy.get_balance(TEST_UID1) == 50
    assert economy.get_balance(TEST_UID2) == 50


def test_transfer_not_enough_balance(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(TEST_UID1) == 0
    assert economy.get_balance(TEST_UID2) == 0

    assert not economy.transfer(TEST_UID1, TEST_UID2, 100)


def test_transfer_negative_amount(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    assert economy.get_balance(TEST_UID1) == 0
    assert economy.get_balance(TEST_UID2) == 0

    assert not economy.transfer(TEST_UID1, TEST_UID2, -100)


def test_get_transaction_record(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    economy.earn(TEST_UID1, 100)
    economy.earn(TEST_UID2, 50)
    economy.earn(TEST_UID1, 100)
    economy.earn(TEST_UID2, 50)
    economy.earn(TEST_UID1, 100)

    records_uid1 = economy.get_transactions(TEST_UID1)
    assert len(records_uid1) == 3
    for record in records_uid1:
        assert record.user_id == TEST_UID1
        assert record.amount == 100

    records_uid2 = economy.get_transactions(TEST_UID2)
    assert len(economy.get_transactions(TEST_UID2)) == 2
    for record in records_uid2:
        assert record.user_id == TEST_UID2
        assert record.amount == 50


def test_get_transaction_record_with_limit(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    economy.earn(TEST_UID1, 100)
    economy.earn(TEST_UID1, 100)
    economy.earn(TEST_UID1, 100)

    records = economy.get_transactions(TEST_UID1, 1)
    assert len(records) == 1


def test_get_transaction_record_empty(db_initialize: Callable) -> None:
    from canrotbot.essentials.libraries import economy

    db_initialize()

    records = economy.get_transactions(TEST_UID1, 1)
    assert len(records) == 0
