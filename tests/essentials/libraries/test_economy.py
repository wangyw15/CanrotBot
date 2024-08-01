from typing import Callable


def test_create_table(db_initialize: Callable) -> None:
    from storage.database import Base
    from essentials.libraries import economy

    db_initialize()

    assert economy.data.Account.__tablename__ in Base.metadata.tables
    assert economy.data.Transaction.__tablename__ in Base.metadata.tables


def test_earn(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance("test") == 0

    economy.earn("test", 100)
    assert economy.get_balance("test") == 100
    
    economy.earn("test", 100)
    assert economy.get_balance("test") == 200


def test_pay(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance("test") == 0

    economy.earn("test", 100)
    assert economy.get_balance("test") == 100

    economy.pay("test", 50)
    assert economy.get_balance("test") == 50


def test_transfer(db_initialize: Callable) -> None:
    from essentials.libraries import economy

    db_initialize()

    assert economy.get_balance("test1") == 0
    assert economy.get_balance("test2") == 0

    economy.earn("test1", 100)
    assert economy.get_balance("test1") == 100

    economy.transfer("test1", "test2", 50)
    assert economy.get_balance("test1") == 50
    assert economy.get_balance("test2") == 50
