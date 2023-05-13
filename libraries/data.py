from nonebot import get_driver, logger
import sqlite3

from .config import canrot_config

_db = sqlite3.connect(canrot_config.canrot_data)
_cursor = _db.cursor()

def execute_sql_on_data(sql: str) -> list[list]:
    temp_c = _cursor.execute(sql)
    ret: list[list] = []
    col_name: list[str] = [t[0] for t in temp_c.description]
    ret.append(col_name)
    ret += temp_c.fetchall()
    _db.commit()
    return ret

_driver = get_driver()
@_driver.on_shutdown
async def _():
    _db.commit()
    _db.close()
    logger.info('Closed data database')
