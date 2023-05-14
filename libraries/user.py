# puid (platform user id): qq_1234567890, kook_1234567890, ...
import uuid

from .data import _cursor, _db

# initialize the database
def init():
    '''initialize the database'''
    _cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        puid TEXT PRIMARY KEY NOT NULL UNIQUE,
        uid TEXT NOT NULL
    )''')
    _db.commit()

init()

def puid_user_exists(puid: str) -> bool:
    '''check if a user with the puid exists'''
    temp_c = _cursor.execute(f'SELECT * FROM users WHERE puid == "{puid}"')
    ret = len(temp_c.fetchall()) != 0
    return ret

def uid_user_exists(uid: str) -> bool:
    '''check if a user with the uid exists'''
    temp_c = _cursor.execute(f'SELECT * FROM users WHERE uid == "{uid}"')
    ret = len(temp_c.fetchall()) != 0
    return ret

def bind(puid: str, uid: str) -> bool:
    '''bind a puid to a uid'''
    if puid_user_exists(puid):
        return False
    _cursor.execute(f'INSERT INTO users (puid, uid) VALUES ("{puid}", "{uid}")')
    _db.commit()
    return True

def unbind(puid: str) -> bool:
    '''unbind a puid from a uid'''
    if not puid_user_exists(puid):
        return False
    _cursor.execute(f'DELETE FROM users WHERE puid == "{puid}"')
    _db.commit()
    return True

def register(puid: str) -> str:
    '''register a new user and set the puid as the account owner'''
    if puid_user_exists(puid):
        return ''
    uid = uuid.uuid4()
    _cursor.execute(f'INSERT INTO users (puid, uid) VALUES ("{puid}", "{uid}")')
    _db.commit()
    return str(uid)

def get_uid(puid: str) -> str:
    '''get the uid of a puid'''
    if not puid_user_exists(puid):
        return ''
    temp_c = _cursor.execute(f'SELECT uid FROM users WHERE puid == "{puid}"')
    data: list[list[str]] = temp_c.fetchall()
    return data[0][0]

def get_bind_by_uid(uid: str) -> list[str]:
    return [x[0] for x in _cursor.execute(f'SELECT puid FROM users WHERE uid == "{uid}"').fetchall()]

def get_bind_by_puid(puid: str) -> list[str]:
    return get_bind_by_uid(get_uid(puid))

def set_data(uid: str, key: str, value: str):
    '''set data to a user'''
    _cursor.execute(f'CREATE TABLE IF NOT EXISTS "{uid}" (key TEXT NOT NULL UNIQUE, value TEXT NOT NULL)')
    _cursor.execute(f'REPLACE INTO "{uid}" (key, value) VALUES ("{key}", "{value}")')
    _db.commit()

def get_data_by_uid(uid: str, key: str) -> str:
    '''get data from a user'''
    if not uid_user_exists(uid):
        return ''
    try:
        data: list[list[str]] = _cursor.execute(f'SELECT value FROM "{uid}" WHERE key == "{key}"').fetchall()
        return data[0][0]
    except IndexError:
        return ''

def remove_data(uid: str, key: str):
    '''remove data from a user'''
    if not puid_user_exists(uid):
        return
    _cursor.execute(f'DELETE FROM "{uid}" WHERE key == "{key}"')
    _db.commit()

def get_all_data(uid: str) -> dict[str, str]:
    '''get all data from a user'''
    temp_c = _cursor.execute(f'SELECT * FROM "{uid}"')
    data: list[list[str]] = temp_c.fetchall()
    ret: dict[str, str] = {}
    for i in data:
        ret[i[0]] = i[1]
    return ret
