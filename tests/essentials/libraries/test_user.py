from typing import Callable


def test_create_user_tables(db_initialize: Callable) -> None:
    from storage.database import Base
    from essentials.libraries import user

    db_initialize()

    assert user.data.User.__tablename__ in Base.metadata.tables
    assert user.data.Bind.__tablename__ in Base.metadata.tables
