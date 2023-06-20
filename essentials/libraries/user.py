# puid (platform user id): qq_1234567890, kook_1234567890, ...
import re
import uuid
from sqlite3 import OperationalError

from nonebot.adapters import Bot, Event

from .data import data_cursor, data_db
from adapters import unified


# initialize the database
def init():
    """initialize the database"""
    data_cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        puid TEXT PRIMARY KEY NOT NULL UNIQUE,
        uid TEXT NOT NULL
    )''')
    data_db.commit()


init()


def puid_user_exists(puid: str) -> bool:
    """check if a user with the puid exists"""
    temp_c = data_cursor.execute(f'SELECT * FROM users WHERE puid == "{puid}"')
    ret = len(temp_c.fetchall()) != 0
    return ret


def uid_user_exists(uid: str) -> bool:
    """check if a user with the uid exists"""
    temp_c = data_cursor.execute(f'SELECT * FROM users WHERE uid == "{uid}"')
    ret = len(temp_c.fetchall()) != 0
    return ret


def bind(puid: str, uid: str) -> bool:
    """bind a puid to a uid"""
    if puid_user_exists(puid):
        return False
    data_cursor.execute(f'INSERT INTO users (puid, uid) VALUES ("{puid}", "{uid}")')
    data_db.commit()
    return True


def unbind(puid: str) -> bool:
    """unbind a puid from a uid"""
    if not puid_user_exists(puid):
        return False
    data_cursor.execute(f'DELETE FROM users WHERE puid == "{puid}"')
    data_db.commit()
    return True


def register(puid: str) -> str:
    """register a new user and set the puid as the account owner"""
    if puid_user_exists(puid):
        return ''
    uid = uuid.uuid4()
    data_cursor.execute(f'INSERT INTO users (puid, uid) VALUES ("{puid}", "{uid}")')
    data_db.commit()
    return str(uid)


def get_puid(bot: Bot, event: Event) -> str:
    puid = event.get_user_id()
    if unified.Detector.is_onebot_v11(bot) or unified.Detector.is_onebot_v12(bot) or unified.Detector.is_mirai2(bot):
        puid = 'qq_' + puid
    elif unified.Detector.is_kook(bot):
        puid = 'kook_' + puid
    elif unified.Detector.is_console(bot):
        puid = 'console_0'
    elif unified.Detector.is_qqguild(bot):
        puid = 'qqguild_' + puid
    return puid


def get_uid(puid: str) -> str:
    """get the uid of a puid"""
    if not puid_user_exists(puid):
        return ''
    temp_c = data_cursor.execute(f'SELECT uid FROM users WHERE puid == "{puid}"')
    data: list[list[str]] = temp_c.fetchall()
    return data[0][0]


def check_puid_validation(puid: str) -> bool:
    """检查PUID是否有效"""
    return re.match('^[a-z]+_[0-9]+$', puid) is not None


def get_bind_by_uid(uid: str) -> list[str]:
    return [x[0] for x in data_cursor.execute(f'SELECT puid FROM users WHERE uid == "{uid}"').fetchall()]


def get_bind_by_puid(puid: str) -> list[str]:
    return get_bind_by_uid(get_uid(puid))


def set_data_by_uid(uid: str, key: str, value: str):
    """set data to a user"""
    data_cursor.execute(f'CREATE TABLE IF NOT EXISTS "{uid}" (key TEXT NOT NULL UNIQUE, value TEXT NOT NULL)')
    data_cursor.execute(f'REPLACE INTO "{uid}" (key, value) VALUES ("{key}", "{value}")')
    data_db.commit()


def get_data_by_uid(uid: str, key: str) -> str:
    """get data from a user"""
    if not uid_user_exists(uid):
        return ''
    try:
        data: list[list[str]] = data_cursor.execute(f'SELECT value FROM "{uid}" WHERE key == "{key}"').fetchall()
        return data[0][0]
    except IndexError:
        return ''
    except OperationalError:
        return ''


def remove_data(uid: str, key: str):
    """remove data from a user"""
    if not puid_user_exists(uid):
        return
    data_cursor.execute(f'DELETE FROM "{uid}" WHERE key == "{key}"')
    data_db.commit()


def get_all_data(uid: str) -> dict[str, str]:
    """get all data from a user"""
    temp_c = data_cursor.execute(f'SELECT * FROM "{uid}"')
    data: list[list[str]] = temp_c.fetchall()
    ret: dict[str, str] = {}
    for i in data:
        ret[i[0]] = i[1]
    return ret
