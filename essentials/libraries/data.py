from nonebot import get_driver, logger
import sqlite3

from .config import canrot_config

data_db = sqlite3.connect(canrot_config.canrot_data)
data_cursor = data_db.cursor()


def execute_sql_on_data(sql: str) -> list[list]:
    temp_c = data_cursor.execute(sql)
    ret: list[list] = []
    col_name: list[str] = [t[0] for t in temp_c.description]
    ret.append(col_name)
    ret += temp_c.fetchall()
    data_db.commit()
    return ret


@get_driver().on_shutdown
async def _():
    data_db.commit()
    data_db.close()
    logger.info('Closed data database')
